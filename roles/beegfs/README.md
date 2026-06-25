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
