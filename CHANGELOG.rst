========================
clip.hpc Release Notes
========================

.. contents:: Topics


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
