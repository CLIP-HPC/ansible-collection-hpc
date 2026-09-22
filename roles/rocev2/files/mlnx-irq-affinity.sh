#!/usr/bin/env bash

# Applies NUMA-aware IRQ affinity for every discovered RoCE NIC using the vendor-provided
# set_irq_affinity.sh script (shipped by the mlnx-tools/DOCA-OFED packages, see the clip.hpc.doca
# role). irqbalance actively fights this tuning by rebalancing IRQs across all CPUs, so it must be
# disabled/masked on hosts that run this service.
SET_IRQ_AFFINITY="/usr/sbin/set_irq_affinity.sh"

if [ ! -x "$SET_IRQ_AFFINITY" ]; then
    echo "mlnx-irq-affinity: $SET_IRQ_AFFINITY not found or not executable (requires the mlnx-tools/DOCA-OFED package)" >&2
    exit 1
fi

attempted=0
succeeded=0

for ibdev in /sys/class/infiniband/mlx5_*; do
    netdir="$ibdev/device/net"
    if [ -d "$netdir" ]; then
        for netif in "$netdir"/*; do
            ethname=$(basename "$netif")
            attempted=$((attempted + 1))
            if "$SET_IRQ_AFFINITY" "$ethname"; then
                succeeded=$((succeeded + 1))
            else
                echo "mlnx-irq-affinity: $SET_IRQ_AFFINITY failed for $ethname, skipping" >&2
            fi
        done
    fi
done

if [ "$attempted" -gt 0 ] && [ "$succeeded" -eq 0 ]; then
    echo "mlnx-irq-affinity: none of the $attempted NIC(s) found could have IRQ affinity set" >&2
    exit 1
fi

exit 0
