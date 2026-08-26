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

for ibdev in /sys/class/infiniband/mlx5_*; do
    # Configure TOS for RDMA-CM QPs
    # https://enterprise-support.nvidia.com/s/article/howto-set-egress-tos-dscp-on-rdma-cm-qps
    ibname=$(basename "$ibdev")
    cma_roce_tos -d "$ibname" -t $TOS
    if [ -d "/sys/class/infiniband/$ibname/tc" ]; then
        echo $TOS > "/sys/class/infiniband/$ibname/tc/1/traffic_class"
    fi
    netdir="$ibdev/device/net"
    if [ -d "$netdir" ]; then
        for netif in "$netdir"/*; do
            ethname=$(basename "$netif")
            mlnx_qos -i "$ethname" --trust dscp
        done
    fi
done
