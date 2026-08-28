#!/usr/bin/env bash

#
# For switch classification it doesn't matter — both give DSCP 26, and --trust dscp only looks at the top 6 bits.
#
# The difference is the low 2 bits (ECN):

# 104 = 011010 00 → ECN = 00 (Not-ECT) — routers won't mark, they'll just drop under congestion
# 106 = 011010 10 → ECN = 10 (ECT(0)) — packets are ECN-capable, so switches can CE-mark them and DCQCN works
# Use 106. It's the value in every NVIDIA/vendor reference config, and if you're running DCQCN (which you basically always are with RoCEv2) you want the ECT bit set.
#
# In practice ConnectX hardware sets ECT itself for RoCE traffic regardless, so 104 usually still ends up working — but there's no reason to deviate from 106.
TOS=106
attempted=0
succeeded=0

for ibdev in /sys/class/infiniband/mlx5_*; do
    # Configure TOS for RDMA-CM QPs
    # https://enterprise-support.nvidia.com/s/article/howto-set-egress-tos-dscp-on-rdma-cm-qps
    ibname=$(basename "$ibdev")
    if ! cma_roce_tos -d "$ibname" -t $TOS; then
        echo "mlnx-roce-qos: cma_roce_tos failed for $ibname, skipping device" >&2
        continue
    fi
    if [ -d "/sys/class/infiniband/$ibname/tc" ]; then
        echo $TOS > "/sys/class/infiniband/$ibname/tc/1/traffic_class"
    fi
    netdir="$ibdev/device/net"
    if [ -d "$netdir" ]; then
        for netif in "$netdir"/*; do
            ethname=$(basename "$netif")
            attempted=$((attempted + 1))
            # Internal NVLink/fabric ConnectX-7 NICs (e.g. on GPU nodes) expose a
            # netdev but don't support DSCP-based trust classification. Skip those
            # instead of failing the whole service.
            if mlnx_qos -i "$ethname" --trust dscp; then
                succeeded=$((succeeded + 1))
            else
                echo "mlnx-roce-qos: $ethname does not support 'trust dscp', skipping" >&2
            fi
        done
    fi
done

if [ "$attempted" -gt 0 ] && [ "$succeeded" -eq 0 ]; then
    echo "mlnx-roce-qos: none of the $attempted NIC(s) found could be configured for DSCP trust" >&2
    exit 1
fi

exit 0
