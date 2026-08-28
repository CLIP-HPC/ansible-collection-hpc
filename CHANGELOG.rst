========================
clip.hpc Release Notes
========================

.. contents:: Topics


v3.7.1
======
- rocev2: Run the QoS service enable/start step in a new ``configure.yml`` after ``dcbx.yml`` instead of during ``install.yml``, since starting the service before DCBX/LLDP is configured can fail with "Priority trust state is not supported on your system"
- rocev2: Make ``mlnx-roce-qos.sh`` skip NICs that don't support ``cma_roce_tos`` or ``mlnx_qos --trust dscp`` (e.g. internal NVLink/fabric ConnectX-7 NICs on GPU nodes) instead of failing the whole service

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
