========================
clip.hpc Release Notes
========================

.. contents:: Topics


v3.10.0
=======
- multirail: Add a route for each of the interface's subnets to its routing table (IPv4 and IPv6), so traffic from a rail address to a host in the same subnet goes out directly instead of through the gateway
- multirail: Set the ARP and ``rp_filter`` sysctls also per interface, since the kernel uses the higher of the ``all`` and the per-interface value and the ``all`` setting alone left ``rp_filter=1`` (strict) on the rail NICs. Change the ``rp_filter`` default from ``0`` to ``2`` (loose) and add ``accept_local=1`` (``multirail_net_accept_local``) for traffic between the rails of the same host
- multirail: Move ``multirail_net_*`` and ``multirail_nmcli_connection_prefix`` from ``vars`` to ``defaults`` so they can be overridden, and add ``multirail_ipv4_gateways`` to set the IPv4 gateway per interface instead of assuming the first usable address of the subnet
- multirail: Add a routing rule for every IPv4 address (including secondaries) and every global IPv6 address of an interface instead of only the first one
- multirail: Name the routing tables in ``/etc/iproute2/rt_tables.d/multirail.conf`` and remove the block previously written to ``rt_tables`` (``/usr/share/iproute2/rt_tables`` on EL10, which belongs to the iproute package)
- multirail: Verify after configuration that traffic from each interface's IPv4 address is routed out of that interface (``multirail_verify``, default ``true``). Both interfaces are now reapplied by one ``Reapply multirail interfaces`` handler

v3.9.0
======
- dell_dsu: Add role to install Dell System Update (DSU), inventory/preview firmware and driver updates on Dell servers, and optionally apply them (``dell_dsu_apply``, with opt-in reboot via ``dell_dsu_reboot``). Also add standalone ``dell_dsu_report`` and ``dell_dsu_update`` playbooks
- rocev2: Add ``rocev2_ethtool_ring_rx``/``rocev2_ethtool_ring_tx`` to manage the ethtool ring buffer sizes on the NetworkManager connections of the discovered RoCE NICs (``/sys/class/infiniband/mlx5_*``), live-applied via ``ethtool -G``; an empty string removes an existing override. Unset by default, so ring sizes are left untouched
- rocev2: Add opt-in IRQ affinity optimization (``rocev2_irq_affinity_enabled``, default ``false``, ``rocev2_irq_affinity_service_state``) that masks ``irqbalance`` and runs the vendor ``set_irq_affinity.sh`` for every RoCE NIC through a new ``mlnx-irq-affinity`` systemd service
- beegfs: Add ``beegfs_conn_auth_beegfs_group`` (default ``false``) to make ``/etc/beegfs/conn.auth`` owned by ``root:beegfs`` with mode ``0640`` instead of ``root:root`` with mode ``0600``
- beegfs: Add ``beegfs_conn_interfaces_addr``/``beegfs_conn_interfaces_protocol`` to restrict the ``connInterfacesFile`` entries by address and/or IP protocol (BeeGFS >= 8.2 advanced filter syntax), unset by default. Also document that ``beegfs_interfaces`` entries are written verbatim and fix the OSS interfaces fallback, which referenced an undefined variable when a ``beegfs_oss`` entry had no explicit ``interfaces``
- slurm: Retry the initial ``sacctmgr`` cluster registration on the controller (``slurm_dbd_connect_retries``, default 30 x 10s) so a controller configured concurrently with the database node tolerates slurmdbd not being up yet
- beegfs: Give the metadata service its own ``connInterfacesFile`` (``beegfs_meta_conn_interfaces_file``) with the NIC(s) local to ``beegfs_meta_tune_bind_to_numa_zone`` first, the same way each ``beegfs_oss`` entry's interfaces are ordered, instead of the global file's ``beegfs_interfaces`` order - the meta service could otherwise prefer a NIC on the other NUMA zone than the one it's bound to. Adds ``beegfs_meta_interfaces`` to override the list. Changes ``connInterfacesFile`` in ``beegfs-meta.conf``, so the meta service restarts once on upgrade, and now fails, like the OSS services already did, if the meta service's preferred NIC isn't NUMA-local
- beegfs: Add ``beegfs_numa_nic_fallback`` (default ``true``, the previous behavior) to choose whether the NUMA-bound meta and OSS services keep the non-local NIC(s) after the local one(s) as an HA fallback, or (``false``) use only NUMA-local NIC(s) - every NIC is then validated to be NUMA-local, and a service without a local NIC fails the run instead of getting an empty ``connInterfacesFile``
- beegfs: Add ``beegfs_meta_tune_num_comm_slaves`` (``tuneNumCommSlaves``) and ``beegfs_meta_tune_default_chunk_size``/``beegfs_meta_tune_default_num_stripe_targets`` (``tuneDefaultChunkSize``/``tuneDefaultNumStripeTargets``) to the metadata server tunings, unset by default to keep the package defaults. The two stripe settings only apply when the root directory is created on a new file system

v3.8.0
======
- rdma_exporter: Add role to install and manage the Prometheus ``rdma_exporter``, exposing RDMA (InfiniBand/RoCE) NIC statistics via a pinned, checksum-verified release binary and a systemd service, with optional firewalld integration and optional upstream tooling to enable mlx5/QP hardware counters

v3.7.2
======
- slurm: Stop passing ``RealMemory`` from the ``slurmd_topology`` local fact into the dynamic-node ``--conf`` string, since slurmd already auto-detects it at registration (``-Z``) when it isn't explicitly overridden
- slurm: Start slurmd with ``--parameters=numa_node_as_socket`` for both dynamic and static nodegroups, so the running daemon's own topology self-detection matches the NUMA-as-socket accounting already used to populate ``slurm.conf``'s ``Sockets``/``CoresPerSocket``/``ThreadsPerCore`` for static nodegroups (via ``slurmd_topology.fact``, which also runs with ``--parameters=numa_node_as_socket``). This restarts slurmd fleet-wide; on hardware where NUMA-domain count differs from physical-socket count this is expected to resolve topology mismatches, but should be verified on such hardware after rollout

v3.7.1
======
- rocev2: Run the QoS service enable/start step in a new ``service.yml`` after ``dcbx.yml`` instead of during ``install.yml``, since starting the service before DCBX/LLDP is configured can fail with "Priority trust state is not supported on your system"
- rocev2: Make ``mlnx-roce-qos.sh`` skip individual NICs that don't support ``cma_roce_tos`` or ``mlnx_qos --trust dscp`` (e.g. internal NVLink/fabric ConnectX-7 NICs on GPU nodes) instead of failing the whole service, while still failing the service if none of the NICs found could be configured

v3.7.0
======
- smartctl_exporter: Add role to install and manage the Prometheus ``smartctl_exporter``, exposing S.M.A.R.T. disk health metrics via a pinned, checksum-verified release binary and a systemd service

v3.6.1
======
- beegfs: Add ``numa_zone`` per entry in ``beegfs_oss`` and ``beegfs_meta_tune_bind_to_numa_zone`` to configure ``tuneBindToNumaZone`` on the oss and meta services for NUMA systems, and fail early if the resolved devices or preferred NIC do not match the configured NUMA zone
- beegfs: Auto-discover ``devices``/``interfaces`` for any ``beegfs_oss`` entry that omits them, based on that entry's ``numa_zone`` and the new ``beegfs_disk_device_regex`` default, so OSS ports can be configured statically, dynamically, or a mix of both on the same host - fails early if the OS disk can't be resolved, if an entry has neither ``devices`` nor ``numa_zone``, or if discovery would assign the same device to more than one entry
- beegfs: Make ``beegfs_meta_dev``/``beegfs_oss[*].devices`` auto-discovery label-first and reboot-safe - an already-formatted disk is identified by its persistent filesystem label (``beegfs_meta_dev_label``/``ST-<port>-<idx>``) rather than by its current, PCIe-probe-order-dependent device name, and the format tasks in ``meta.yml``/``fs.yml`` skip reformatting any device resolved this way unless ``beegfs_force_format`` is set. Fresh NUMA/name-based discovery now only ever runs for genuinely unprovisioned disks (first bootstrap). Also consolidates the disk/NUMA discovery previously duplicated between this role and its consumers into shared, importable task files (``disk_facts.yml``, ``resolve_meta_device.yml``)

v3.6.0
======
- slurm: Add dynamic node support (``slurm_dynamic_nodes``, per-nodegroup ``dynamic`` key): dynamic nodegroups are omitted from ``slurm.conf`` and their slurmd self-registers with the controller via ``-Z --conf``, so compute nodes booting via ansible-init no longer require a controller reconfigure first
- slurm: Render ``MaxNodeCount`` (``slurm_max_node_count``, default 1024) and ``TreeWidth=65533`` when any nodegroup is dynamic

v3.5.5
======
- beegfs: Add license file support to the management role, deploying it to ``/etc/beegfs/license.pem`` and reloading it via ``beegfs license --reload`` when the mgmt service is already running
- beegfs: Finish multi-client-mount support cleanup, including the ``beegfs_client_mounts`` rename, per-mount client config files, and the documented per-mount ``mgmt_host`` override
- beegfs: Fix a crash in the management role when no BeeGFS license is configured
- beegfs: Remove the GDS EXPORT_SYMBOL workaround now that it is fixed upstream in BeeGFS >= 8.5

v3.5.4
======
- slurm: Fall back to any inventory-group host with cached facts for the slurm.conf topology lookup when ``--limit`` excludes the play batch
- rocev2: Ensure the MLNX RoCE QoS service is enabled and started after install

v3.5.3
======
- beegfs: Fix BeeGFS client DKMS source directory detection and Nvfs.c path in the GDS EXPORT_SYMBOL workaround

v3.5.2
======
- beegfs: Work around GDS EXPORT_SYMBOL issue in client module and enable the workaround by default
- beegfs: Fix non-boolean when condition in GDS workaround check on ansible-core 2.19+

v3.5.1
======
- rocev2: Fix DCBX task to handle non-NIC devices and ensure at least one configurable NIC
- doca: Bump doca_version to 3.4.0 and improve NVIDIA include path detection
- beegfs/filter plugins: Add filter plugin DOCUMENTATION and beegfs role README to unblock Automation Hub publishing

v2.1.0
=====
- Add support for SLURM 24.02.xx
- Fix NVIDIA row remapping failure nhc tests

v2.0.0
======

Release Summary
---------------

- Add support for newer ansible versions
