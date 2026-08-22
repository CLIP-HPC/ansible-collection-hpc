# clip.hpc.beegfs Role

Provision an existing cluster to support [BeeGFS](https://www.beegfs.io/) management, metadata, object storage server, and client roles.

## Role Variables

- `beegfs_state`: Whether to create or destroy the BeeGFS cluster. One of `present` or `absent`. Default: `present`.
- `beegfs_enable`: Dict controlling which BeeGFS services are enabled on the target host.
  - `mgmt`: Enable BeeGFS management service. Default: `false`.
  - `meta`: Enable BeeGFS metadata service. Default: `false`.
  - `oss`: Enable BeeGFS object storage service. Default: `false`.
  - `mon`: Enable BeeGFS monitoring service. Default: `false`.
  - `client`: Enable BeeGFS client. Default: `false`.
  - `tuning`: Enable BeeGFS tuning. Default: `false`.
- `beegfs_interfaces`: List of network interfaces in order of preference. Leaving empty means InfiniBand and RDMA-enabled devices are preferred. Default: `[]`.
- `beegfs_target_id_multiplier`: Multiplier applied to node ID when computing target IDs. Default: `100`.
- `beegfs_node_num_id`: Numeric node ID used for target ID calculation.
- `beegfs_oss`: Dict of object storage server configurations, keyed by name.
- `beegfs_oss_path_prefix`: Filesystem path prefix for OSS mount points.
- `beegfs_license_content`: Content of the BeeGFS license file (obtained from ThinkParQ). Deployed to `/etc/beegfs/license.pem` only on the management node. Leave unset to run without a license. See the [BeeGFS licensing docs](https://doc.beegfs.io/latest/advanced_topics/licensing.html). Note: unsetting this does not remove a previously deployed license file.
- `beegfs_client_mounts`: List of client mounts to configure on this host. Default: `[]`. Each item:
  - `path`: Mount path. Must be unique per mount.
  - `port`: `connClientPort` for this mount. Must be unique per mount.
  - `mgmt_host`: Optional. Overrides `beegfs_mgmt_host` for this mount, for connecting to a different BeeGFS cluster.
  When more than one mount is configured, each gets its own `/etc/beegfs/beegfs-client-<port>.conf`; with a single mount, the default `/etc/beegfs/beegfs-client.conf` is used as-is.
- `beegfs_nvfs_gds_export_symbol_workaround`: Apply the workaround for [ThinkParQ/beegfs#123](https://github.com/ThinkParQ/beegfs/issues/123), where GPUDirect Storage (GDS) is reported as unsupported on kernels that restrict `symbol_get()` to GPL-exported symbols. Patches the BeeGFS client DKMS source to export its nvfs registration hooks with `EXPORT_SYMBOL_GPL` and rebuilds the module. Only takes effect when GDS/NVFS support is being built (`beegfs_nvfs_include_path` is set), so it is a no-op otherwise. If the beegfs module is already loaded, unmount all BeeGFS filesystems and reload the module (or reboot) for the change to take effect. Fixed upstream in BeeGFS >= 8.5. Default: `true`.

## Example Playbook

```yaml
- name: Deploy BeeGFS cluster
  hosts: beegfs_nodes
  roles:
    - role: clip.hpc.beegfs
      vars:
        beegfs_state: present
        beegfs_enable:
          mgmt: true
          meta: true
          oss: true
          client: true
```

### Licensing

Pass the license file content in via Ansible Vault rather than committing it in plaintext:

```yaml
- name: Deploy BeeGFS cluster
  hosts: beegfs_nodes
### Multiple client mounts

A host can mount more than one BeeGFS filesystem, including filesystems served by different management hosts:

```yaml
- name: Deploy BeeGFS clients
  hosts: beegfs_client_nodes
  roles:
    - role: clip.hpc.beegfs
      vars:
        beegfs_enable:
          mgmt: true
        beegfs_license_content: "{{ vault_beegfs_license_content }}"
          client: true
        beegfs_mgmt_host: "{{ groups['cluster_beegfs_mgmt'] | first }}"
        beegfs_client_mounts:
          - path: "/mnt/beegfs"
            port: 8004
          - path: "/mnt/beegfs-other"
            port: 8005
            mgmt_host: "beegfs-mgmt.other-cluster.example.org"
```
