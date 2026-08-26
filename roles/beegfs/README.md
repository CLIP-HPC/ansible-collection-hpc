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
- `beegfs_oss`: Dict of object storage server configurations, keyed by port. Each entry:
  - `numa_zone`: Optional. NUMA zone this OSS is local to. Configures `tuneBindToNumaZone` for this OSS - a host can run multiple OSS services bound to different NUMA zones. Also required to auto-discover `devices`/`interfaces` when they're omitted (below). Fails if the resolved devices or the preferred (first) interface are attached to a different NUMA node.
  - `devices`: Optional. List of block devices for this OSS. If omitted, devices are resolved **label-first**: any device already labeled `ST-<port>-<index>` from a previous run is reused regardless of its current name (device names aren't stable across reboots - see "Reboot-safe device resolution" below), and only genuinely unlabeled slots are filled from fresh discovery (disks matching `beegfs_disk_device_regex` attached to `numa_zone`, excluding the OS disk, `beegfs_meta_dev`, and any device explicitly claimed by another `beegfs_oss` entry) - `numa_zone` is required in that case.
  - `interfaces`: Optional. Overrides `beegfs_interfaces` for this OSS. If omitted and `numa_zone` is set, this is `beegfs_interfaces` reordered so the NIC(s) local to `numa_zone` come first.

  A deployment can configure OSS ports/devices/interfaces statically, rely on NUMA-zone-based auto-discovery, or mix both on the same host.
- `beegfs_disk_device_regex`: Regex matching candidate whole-disk device names eligible for BeeGFS OSS auto-discovery. Only used for `beegfs_oss` entries that omit `devices`. Default: `'^(nvme[0-9]+n[0-9]+|vd[a-z]|sd[a-z])$'`.
- `beegfs_meta_dev`: Optional. Metadata device path (e.g. `/dev/sdb`). If omitted and `beegfs_enable.meta` is true, it's resolved the same label-first way as `beegfs_oss` devices (see below), using `beegfs_meta_dev_label`.
- `beegfs_meta_tune_bind_to_numa_zone`: Optional. NUMA zone to bind the metadata service to on NUMA systems, since only one metadata device/service is supported per host. Auto-populated when `beegfs_meta_dev` is auto-discovered.
- `beegfs_oss_path_prefix`: Filesystem path prefix for OSS mount points.
- `beegfs_license_content`: Content of the BeeGFS license file (obtained from ThinkParQ). Deployed to `/etc/beegfs/license.pem` only on the management node. Leave unset to run without a license. See the [BeeGFS licensing docs](https://doc.beegfs.io/latest/advanced_topics/licensing.html). Note: unsetting this does not remove a previously deployed license file.
- `beegfs_client_mounts`: List of client mounts to configure on this host. Default: `[]`. Each item:
  - `path`: Mount path. Must be unique per mount.
  - `port`: `connClientPort` for this mount. Must be unique per mount.
  - `mgmt_host`: Optional. Overrides `beegfs_mgmt_host` for this mount, for connecting to a different BeeGFS cluster.
  Each mount gets its own `/etc/beegfs/beegfs-client-<port>.conf`.

### Reboot-safe device resolution

`/dev/nvmeXnY` names are assigned by asynchronous PCIe probe order and are **not** stable across
reboots. Picking "which disk is meta" / "which disks are OSS target N" fresh every run, purely from
current device names, risks reformatting the wrong physical disk after a renumbering event.

Every disk this role formats gets a durable filesystem label at format time (`beegfs_meta_dev_label`
for meta, `ST-<port>-<index>` per OSS target). Labels live in the on-disk superblock and survive
reboots; `/dev/disk/by-label/<label>` always resolves to whatever device currently holds that
label. `beegfs_meta_dev`/`beegfs_oss[*].devices` auto-discovery checks for an existing label
**first** - fresh NUMA/name-based discovery only ever runs for a slot that was never labeled (first
bootstrap, or a genuinely new disk). The format tasks in `meta.yml`/`fs.yml` skip reformatting any
device that was resolved from an existing label, regardless of its current name, unless
`beegfs_force_format` is set - which reformats the *label-resolved* device in place, never a
fresh-discovery guess. Moving an already-labeled role to different physical hardware on purpose
requires clearing the stale label out-of-band (e.g. `wipefs`) first; this is not something
`beegfs_force_format` does automatically.

This is only relevant to entries that omit `devices`/`beegfs_meta_dev` - statically configured
paths are used exactly as given and never go through label resolution.

### Public task files for consumers with their own NUMA-zone policy

A consumer that needs to decide its own policy for *how many* OSS ports to create (e.g. one per
NUMA zone with disks, on a schedule it controls) rather than declaring the full `beegfs_oss` dict
statically can reuse the role's own disk/NUMA discovery instead of reimplementing it, via
`ansible.builtin.import_role` with `tasks_from`:

```yaml
- name: Resolve the metadata device and shared disk/NUMA facts
  ansible.builtin.import_role:
    name: clip.hpc.beegfs
    tasks_from: resolve_meta_device
    # -> beegfs_meta_dev, beegfs_meta_dev_name, beegfs_meta_already_provisioned,
    #    beegfs_meta_tune_bind_to_numa_zone, beegfs_candidate_disk_names,
    #    beegfs_disk_numa_map, beegfs_disk_groups (NUMA-grouped candidate disks)
```

Build `beegfs_oss` from `beegfs_disk_groups` (one entry per zone with non-metadata disks, however
many ports/port-numbers your deployment wants), leaving `devices`/`interfaces` unset - the role's
own OSS device/interface auto-discovery (triggered automatically when the role runs) fills them in
label-first, exactly as described above.

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
  roles:
    - role: clip.hpc.beegfs
      vars:
        beegfs_enable:
          mgmt: true
        beegfs_license_content: "{{ vault_beegfs_license_content }}"
```

### Multiple client mounts

A host can mount more than one BeeGFS filesystem, including filesystems served by different management hosts:

```yaml
- name: Deploy BeeGFS clients
  hosts: beegfs_client_nodes
  roles:
    - role: clip.hpc.beegfs
      vars:
        beegfs_enable:
          client: true
        beegfs_mgmt_host: "{{ groups['cluster_beegfs_mgmt'] | first }}"
        beegfs_client_mounts:
          - path: "/mnt/beegfs"
            port: 8004
          - path: "/mnt/beegfs-other"
            port: 8005
            mgmt_host: "beegfs-mgmt.other-cluster.example.org"
```
