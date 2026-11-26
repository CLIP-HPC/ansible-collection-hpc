========================
clip.hpc Release Notes
========================

.. contents:: Topics


v3.24.0
=======
- rocev2: **Breaking:** Only reboot after changing the MLX firmware (LLDP DCBX) settings with ``rocev2_reboot: true`` (new variable, default ``false``). The role rebooted the host right away, on every affected host of the play at once, and a check-mode run didn't show it. Without ``rocev2_reboot``, the role now sets the fact ``rocev2_reboot_required``, adds a line to ``/run/reboot-required`` and prints the devices and settings it changed, so the caller can reboot through its own path, such as ``scontrol reboot ASAP``. In check mode it prints the settings it would change and that they need a reboot. Set ``rocev2_reboot: true`` to keep the automatic reboot
- doca: **Breaking:** Only reboot after installing the DOCA packages with ``doca_reboot: true`` (new variable, default ``false``). Without it, the role now sets the fact ``doca_reboot_required``, adds a line to ``/run/reboot-required`` and prints that a reboot is needed, also in check mode. Set ``doca_reboot: true`` to keep the automatic reboot

v3.23.1
=======
- beegfs: With ``beegfs_state: absent``, stop ``beegfs-oss-tuning.service`` together with the other BeeGFS services. The item was listed without the ``.service`` suffix, so it never matched the ``service_facts`` keys and was always skipped, leaving the service running

v3.23.0
=======
- beegfs: **Breaking:** OSS device auto-discovery now resolves every existing ``ST-<port>-<index>`` label first, for all ports, and the labels set how many devices a port has, instead of the number of disks in the port's ``numa_zone``. Labeled devices outside the zone filled extra slots of the first port, a device labeled for a later port could be taken by an earlier one, and the remaining slots took unlabeled disks that were then formatted next to the live targets. A device labeled for any port is no longer picked for another port or as the metadata device. A port with labels only gets unlabeled disks with ``beegfs_oss_discovery_expand`` (new variable, default ``false``), which fills slots without a labeled device and adds new disks; without it, unlabeled disks in the zone stay unused and the role fails if a slot below the port's highest label has no device. Set it for the run that adds or replaces disks
- beegfs: Leave zero-size, removable, and USB-attached disks out of metadata and OSS device auto-discovery. Cisco CIMC/vKVM virtual media (``sda``-``sdc``, 0 bytes) matched ``beegfs_disk_device_regex`` and were planned as new storage targets
- beegfs: Read the NUMA node of a non-NVMe candidate disk from the closest PCI device in its sysfs path (HBA, virtio controller), and leave a disk whose NUMA node can't be read out of discovery. It was read from ``/sys/class/block/<disk>/device/numa_node``, which SCSI and virtio disks don't have, so every such disk was put in zone 0
- beegfs: An OSS device resolved from its existing label that is attached to another NUMA node than its port's ``numa_zone`` now gives a warning instead of failing the run, since the device keeps its port
- beegfs: With ``beegfs_numa_nic_fallback``, a metadata service or OSS port whose preferred NIC is on another NUMA node than its ``tuneBindToNumaZone`` now gives a warning instead of failing when none of its NICs and none of ``beegfs_interfaces`` is on that NUMA node. A host with all BeeGFS NICs on one NUMA node couldn't run a service on the other. It still fails when a local NIC exists, and names it
- beegfs: Order and check the metadata service's NICs before formatting the metadata device and running ``beegfs-setup-meta``. A failing check left a fresh host with a formatted, set-up metadata target

v3.22.0
=======
- slurm: Probe the node topology with ``slurmd -C --parameters=numa_node_as_socket`` in the role, with a 60 s task timeout, and write it to ``/etc/ansible/facts.d/slurmd_topology.fact`` as static JSON (mode ``0644``) instead of deploying an executable fact script that ran ``slurmd -C`` at every fact gathering. A ``slurmd -C`` stuck in ``sched_setaffinity`` can't be killed, and the script's ``subprocess.run(timeout=30)`` waited for it, so every fact gathering on the node hung until a reboot. A failed or timed-out probe now writes an empty fact (``slurm.conf`` then takes the topology from another host of the nodegroup or from ``ansible_facts``) and the role continues; the probe also runs in check mode. The topology is refreshed on every run of the role, not at every fact gathering. Hosts keep the old script until the role runs on them
- New filter ``clip.hpc.slurmd_topology`` converts ``slurmd -C`` output to a dict

v3.21.1
=======
- rocev2: Run the read-only MLX device discovery (``mst start``, ``mst status``, ``mlxconfig -d <device> q``) and the ``nmcli`` queries for the ethtool ring sizes in check mode too. They were skipped, so with ``--check`` the role found no devices and always failed with "None of the 0 MST device(s) found support mlxconfig queries", and failed on the missing ``rc`` of the skipped ``nmcli`` queries when ``rocev2_ethtool_ring_rx`` or ``rocev2_ethtool_ring_tx`` is set. ``mst start`` loads the MST kernel modules in check mode as well. In check mode on a host without the ``mft`` package, the role skips DCBX discovery and configuration and says so instead of failing on the missing ``mst``
- rocev2: Add ``RemainAfterExit=yes`` to the oneshot units ``mlnx-roce-qos`` and ``mlnx-irq-affinity``, and restart them from the handlers when their script or unit file changes. The units were ``inactive (dead)`` after their script ran, so ``state: started`` re-ran ``mlnx-roce-qos.sh`` (and ``mlnx-irq-affinity.sh`` with ``rocev2_irq_affinity_enabled``) and reported a change on every run. On existing hosts the first run restarts the units once, because their unit files change
- rdma_exporter: Make ``--check`` work on hosts without the exporter, and stop reporting the upstream files as changed in check mode. In check mode the role now skips downloading, extracting and installing a release whose download or extraction directory doesn't exist yet, and skips enabling and starting ``rdma_exporter`` (and ``rdma-hardware-counters``) and the restart handler when their unit file is new or changed. It failed with "Destination /usr/local/src/rdma_exporter does not exist" and "Could not find the requested service". The upstream unit, and with ``rdma_exporter_manage_hardware_counters`` the enablement script, unit and udev rule, are fetched with ``uri``, also in check mode, and written with ``copy``. ``get_url`` only sent a HEAD request in check mode, so ``/etc/systemd/system/rdma_exporter.service`` showed as changed on every run
- smartctl_exporter: Make ``--check`` work on hosts without the exporter. In check mode the role now skips downloading, extracting and installing a release whose download directory doesn't exist yet, and skips enabling and starting ``smartctl_exporter`` and the restart handler when its unit file is new or changed, instead of failing with "Could not find the requested service"
- slurm: Run ``scontrol show config`` in check mode too. It was skipped, so the diff showed ``/etc/ansible/facts.d/slurm.fact`` being replaced with ``{}`` on every Slurm host. In check mode a failing ``scontrol``, such as on a host where Slurm isn't installed yet, skips the fact file instead of failing
- beegfs: Run ``ofed_info -s`` in check mode too. It was skipped with ``rc: 0``, so on hosts without OFED the diff showed a false ``OFED_INCLUDE_PATH`` change in ``beegfs-client-build.mk``

v3.21.0
=======
- slurm: **Breaking:** Remove ``pam_systemd`` from ``password-auth`` and ``system-auth`` on compute nodes, and stop masking ``systemd-logind``. The `pam_slurm_adopt documentation <https://slurm.schedmd.com/pam_slurm_adopt.html#PAM_CONFIG>`_ has asked to disable ``pam_systemd`` in all files included by sshd or system-auth all along; the advice to also stop and mask ``systemd-logind`` was dropped after Slurm 21.08. Masked nodes stay masked until ``systemd-logind`` is unmasked by hand. With authselect the role edits the templates of the selected custom profile; if a vendor profile such as ``sssd`` is selected, it first creates and selects ``custom/<slurm_authselect_profile>`` (new variable, default ``slurm-adopt``) with the current features. Set ``slurm_authselect_profile`` to the name of a custom profile that other plays manage. Without authselect the role edits the files in ``/etc/pam.d``. SSH logins, ``su`` and ``login`` on compute nodes no longer get a logind session or a user manager

v3.20.0
=======
- multirail: **Breaking:** The default route in each interface's IPv6 table now goes via ``multirail_ipv6_gateways[<interface>]`` (new variable, default ``{}``), or else the first usable address of the interface's first global IPv6 subnet (``<prefix>::1``, OpenStack's default ``gateway_ip``), as IPv4 already does. It was read from the live main-table route learned from router advertisements, which can be missing at first boot and changes while NetworkManager reconnects the interface, so the run after every reconnect, including the role's own handler, rewrote ``ipv6.routes`` and reapplied both interfaces, and a missing route left ``::/0`` out silently. Existing hosts change once, from the router's link-local address to ``<prefix>::1``. Set ``multirail_ipv6_gateways`` where the IPv6 router doesn't have that address. The role now fails for an interface with only ``/128`` IPv6 addresses and no entry in ``multirail_ipv6_gateways``
- multirail: Skip removing the legacy routing table block when ``/etc/iproute2/rt_tables`` doesn't exist. ``blockinfile`` failed on the missing file even with ``state: absent``, so the role failed on EL9 hosts whose iproute package no longer ships it (AlmaLinux 9.7)

v3.19.1
=======
- slurm: With ``slurm_db_data_dir`` set, install the systemd drop-in ``mariadb.service.d/datadir-mount.conf`` with ``RequiresMountsFor=<slurm_db_data_dir>`` and reload systemd before ``geerlingguy.mysql`` starts MariaDB. MariaDB was only ordered after ``network.target``, so with the data directory on NFS it started on the empty mountpoint after a reboot, failed, and slurmdbd couldn't connect until MariaDB was started by hand. New variable ``slurm_db_service_name`` (default ``mariadb``) names the unit and is passed to ``geerlingguy.mysql`` as ``mysql_daemon``. Running MariaDB is not restarted; the ordering applies from the next start

v3.19.0
=======
- slurm: New variable ``slurm_node_features`` (host or group variable, default ``[]``) adds Slurm features to a single node on top of those of its nodegroup, for static nodes in ``slurm.conf`` and for dynamic nodes in ``/etc/sysconfig/slurmd``. Lets a node property such as a MIG layout be set from an inventory group without moving the node to another nodegroup

v3.18.3
=======
- slurm: Leave ``BOOT_TIME`` and ``NEXT_JOB_ID`` out of ``slurm.fact``. They change with every ``slurmctld`` restart and every submitted job, so the role reported a change on every run

v3.18.2
=======
- slurm: Create ``/etc/ansible/facts.d`` with mode ``0755`` instead of ``ugo=rwX`` (``0777``), and own ``slurm.fact`` by ``root`` instead of ``slurm``. Ansible's ``setup`` runs every executable ``*.fact`` file there as root, so any local user, or the ``slurm`` account through ``slurm.fact``, could run code as root at the next fact gathering. The next run of the role fixes the mode on existing hosts; check them for ``*.fact`` files the role doesn't deploy (it deploys ``slurm.fact`` and ``slurmd_topology.fact``)

v3.18.1
=======
- multirail: Configure the NetworkManager connection that is active on each interface instead of the one named ``<prefix> <interface>``. cloud-init binds its ``cloud-init <interface>`` profiles to MAC addresses, so after NICs were swapped between slots the profile named after an interface was active on the other one: the role wrote each interface's routing rules into the other NIC's connection, traffic from an address left through the wrong NIC, and with ``arp_filter`` the host stopped answering ARP for both addresses (no DNS, gateway unreachable). ``multirail_nmcli_connection_prefix`` is now only used for an interface without an active connection

v3.18.0
=======
- beegfs: Add quota support. ``beegfs_enable_quota`` now also sets ``quota-enable`` in ``beegfs-mgmtd.toml`` (it only set the client's ``quotaEnabled`` before), ``beegfs_enforce_quota`` sets ``quota-enforce`` in ``beegfs-mgmtd.toml`` and ``quotaEnableEnforcement`` on metadata and storage servers, and ``beegfs_quota_update_interval`` sets ``quota-update-interval``. Settings that are off are removed from the config instead of written as ``false``, so hosts without quota keep their config unchanged. See the role README for enabling quota on an existing file system (``beegfs-fsck --enablequota``)
- beegfs: Storage targets are always mounted with XFS user and group quota accounting (``uqnoenforce,gqnoenforce``), now added in front of ``beegfs_mount_opts`` instead of being part of its default, so overriding ``beegfs_mount_opts`` can no longer drop them. With the default options the mount options are unchanged. The role fails if a storage target's active mount has no user or group accounting, since XFS doesn't turn it on at remount
- beegfs: **Breaking:** Remove ext4 support for storage targets and the ``beegfs_fstype`` variable: storage targets are always XFS. The role fails on storage hosts if ``beegfs_fstype`` is set to anything else. The metadata target still supports ext4 via ``beegfs_meta_fstype``
- beegfs: Add ``beegfs_quota_user_system_ids_min`` and ``beegfs_quota_group_system_ids_min`` for ``quota-user-system-ids-min`` and ``quota-group-system-ids-min`` in ``beegfs-mgmtd.toml``, written only with ``beegfs_enable_quota``. Default: ``0``, so mgmtd tracks every user and group the management host enumerates, including system accounts. ``null`` removes the setting and mgmtd tracks every ID found on the storage targets
- beegfs: Add the ``mgmt_config`` tag for the mgmtd quota settings

v3.17.1
=======
- slurm: Set ``nodename=<short hostname>`` on the ``pam_slurm_adopt`` line on dynamic nodes. They have no ``NodeName`` in ``slurm.conf``, so since Slurm 25.11.2 pam_slurm_adopt looked up job steps under the FQDN from ``gethostname()`` while slurmd runs as ``-N <short hostname>``, and denied SSH to users with running jobs (`SchedMD bug 26042 <https://support.schedmd.com/show_bug.cgi?id=26042>`_). Static nodes are unchanged

v3.17.0
=======
- beegfs: Install ``beegfs-copy`` on clients, so ``beegfs copy`` works there. Without it the CLI fails with ``to use this mode first install the beegfs-copy package``. Hosts that get BeeGFS packages from their own repository (``beegfs_add_repos: false``, e.g. Satellite) need ``beegfs-copy`` available there, otherwise the package install fails

v3.16.0
=======
- beegfs: Add ``beegfs_client_cli_ca_file`` to link ``/etc/beegfs/cert.pem``, the ``beegfs`` CLI's default ``tls-cert-file``, to a CA bundle on clients that aren't the management host. With TLS enabled the CLI failed there with ``reading certificate file failed: open /etc/beegfs/cert.pem: no such file or directory``. Unset by default
- beegfs: Run ``beegfs license --reload`` on the management node when ``/etc/beegfs/license.pem`` changes, so mgmtd loads a new license without a restart. It uses ``beegfs_cli_mgmtd_addr`` and the TLS settings of the alias tasks, and retries while mgmtd is starting

v3.15.0
=======
- beegfs: The alias tasks now set ``BEEGFS_TLS_DISABLE`` from ``beegfs_disable_tls`` instead of always ``true``, so the ``beegfs`` CLI matches mgmtd's ``tls-disable`` and aliases can be set with TLS enabled. **Behavior change:** with the default ``beegfs_disable_tls: false`` the CLI now uses TLS and needs a valid mgmtd certificate
- beegfs: Add ``beegfs_cli_mgmtd_addr`` (default ``<beegfs_mgmt_host>:<beegfs_mgmt_grpc_port>``) and ``beegfs_cli_tls_cert_file`` (default ``/etc/beegfs/cert.pem``) for the alias tasks, so the CLI can reach mgmtd by a name in its certificate and verify it, e.g. against the system trust store for a CA-issued certificate

v3.14.0
=======
- slurm: Add partition slices: a partition in ``slurm_partitions`` can list nodes in ``nodes`` (names or Slurm hostlist expressions, e.g. ``cbe-c3-[13-18]``), so partition membership can change in the variables alone instead of moving nodes between nodegroup inventory groups. The nodes get the feature ``partition_<name>`` and the partition adds ``NodeSet=partition_<name>``. A slice is exclusive unless ``exclusive: false``: its nodes don't get ``nodegroup_<nodegroup>`` and leave the partitions built from their nodegroup. Partitions without ``nodes`` and nodes outside slices render as before. Validation fails if a node is in more than one exclusive slice and warns about slice nodes outside all nodegroups
- slurm: Static nodegroups render one ``NodeName`` line per distinct feature set, so their nodes can be in different slices

v3.13.0
=======
- beegfs: Add an optional per-mount ``auth_secret`` to ``beegfs_client_mounts``, so a client can mount BeeGFS clusters with different auth secrets. It's written to ``/etc/beegfs/conn-<port>.auth`` and set as ``connAuthFile`` of that mount. ``connAuthFile`` of mounts without it is now set explicitly to the global ``/etc/beegfs/conn.auth`` (the BeeGFS 8 package default). Tasks looping over ``beegfs_client_mounts`` use a copy without ``auth_secret``, so the secret isn't logged, also in verbose runs
- beegfs: Fix the documented default of ``beegfs_conn_auth_beegfs_group`` in the README (``false``, not ``true``)

v3.12.1
=======
- beegfs: Install ``beegfs-tools`` (the ``beegfs`` CLI) on management hosts too, not only on clients. The alias tasks run ``/usr/sbin/beegfs`` on ``beegfs_mgmt_host``, so a management host that isn't a client failed with ``No such file or directory: /usr/sbin/beegfs`` (#82). Duplicate package names in the merged per-host list are now removed

v3.12.0
=======
- beegfs: Add ``beegfs_client_conn_rdma_meta_fragment_size`` to configure ``connRDMAMetaFragmentSize`` on the client, with a per-mount ``conn_rdma_meta_fragment_size`` override. Unset by default to preserve the package setting (inherits ``connRDMAFragmentSize``)
- beegfs: Run the NVFS/NVIDIA include path detection also in check mode, so a dry run on GPU nodes with nvidia-fs no longer shows a false diff for ``beegfs-client-build.mk`` that replaces the detected ``NVFS_INCLUDE_PATH``/``NVIDIA_INCLUDE_PATH`` with the commented-out examples

v3.11.0
=======
- beegfs: Add ``beegfs_client_tune_file_cache_buf_size`` to configure ``tuneFileCacheBufSize`` on the client, with a per-mount ``tune_file_cache_buf_size`` override. Unset by default to preserve the package setting

v3.10.0
=======
- beegfs: Format the metadata target as XFS instead of ext4 by default (``beegfs_meta_fstype``) and default ``beegfs_meta_filesystem_opts`` to ``""`` (``mkfs`` defaults), since the previous ext4-specific options don't apply to XFS. **Breaking:** hosts with an existing ext4 metadata target must set ``beegfs_meta_fstype: ext4``, otherwise the mount task fails; set ``beegfs_meta_filesystem_opts`` too if newly formatted ext4 targets should keep the previous options
- beegfs: Add ``beegfs_meta_force_format`` (default ``false``) to reformat only the metadata device - it stops ``beegfs-meta`` and unmounts the device first, and restores the node's ``registrationToken`` afterwards so mgmtd accepts the reformatted node under its old ID - without the full wipe of ``beegfs_force_format`` (mgmtd database, OSS targets, client mounts), e.g. to move an existing metadata target to XFS. Destroys all metadata on the host
- beegfs: Run the OSS setup in parallel across hosts: the per-port/per-device work now loops inside single tasks over flat ``beegfs_oss_ports``/``beegfs_oss_targets`` lists instead of looping ``include_tasks``, which the linear strategy ran one host at a time (a 12-node check-mode run dropped from 575s to 166s). Also wait for udev after ``mkfs`` so the by-label mount doesn't race the new label, and document ``forks``/pipelining for large clusters
- beegfs: Add ``meta_config``/``oss_config``/``client_config`` tags (plus a shared ``config`` tag) to change service tunings without format/setup, an ``interfaces`` tag for every ``connInterfacesFile`` and its NUMA checks, and tag the global ``connInterfacesFile``/``connRDMAInterfacesFile`` with ``client``/``interfaces`` (they were skipped under any ``--tags``). A changed per-port OSS ``connInterfacesFile`` now restarts that storage service
- beegfs: Add ``beegfs_client_remount_on_change`` (default ``false``) to unmount and mount again the client mounts when their config changes, since BeeGFS reads the client config only at mount time
- beegfs: Pass ``--mgmtd-addr <beegfs_mgmt_host>:<beegfs_mgmt_grpc_port>`` (new ``beegfs_mgmt_grpc_port``, default ``8010``) to the ``beegfs`` CLI when setting node/target aliases, so the management host doesn't need a mounted BeeGFS
- multirail: Add a route for each of the interface's subnets to its routing table (IPv4 and IPv6), so traffic from a rail address to a host in the same subnet goes out directly instead of through the gateway
- multirail: Set the ARP and ``rp_filter`` sysctls also per interface, since the kernel uses the higher of the ``all`` and the per-interface value and the ``all`` setting alone left ``rp_filter=1`` (strict) on the rail NICs. Change the ``rp_filter`` default from ``0`` to ``2`` (loose) and add ``accept_local=1`` (``multirail_net_accept_local``) for traffic between the rails of the same host
- multirail: Move ``multirail_net_*`` and ``multirail_nmcli_connection_prefix`` from ``vars`` to ``defaults`` so they can be overridden, and add ``multirail_ipv4_gateways`` to set the IPv4 gateway per interface instead of assuming the first usable address of the subnet
- multirail: Add a routing rule for every IPv4 address (including secondaries) and every global IPv6 address of an interface instead of only the first one
- multirail: Name the routing tables in ``/etc/iproute2/rt_tables.d/multirail.conf`` and remove the block previously written to ``rt_tables`` (``/usr/share/iproute2/rt_tables`` on EL10, which belongs to the iproute package)
- multirail: Verify after configuration that traffic from each interface's IPv4 address is routed out of that interface (``multirail_verify``, default ``true``). Apply the changes with ``nmcli device modify`` (only the routes, routing rules and ``ipv4.never-default``) instead of ``nmcli device reapply``, which failed when the profile had a pending ethtool change, e.g. ring sizes set by ``rocev2``

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
