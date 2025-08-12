#!/bin/bash

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
