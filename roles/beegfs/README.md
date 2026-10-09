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
- `beegfs_interfaces`: List of network interfaces in order of preference, written one per line into `connInterfacesFile`. Leaving empty means InfiniBand and RDMA-enabled devices are preferred. Each entry is written verbatim, so besides plain interface names it also accepts BeeGFS's [advanced filter syntax](https://doc.beegfs.io/latest/advanced_topics/network_configuration.html#configure-allowed-network-interfaces) (e.g. `! eth0, *` or `* * 6`) for name/address/protocol matching. Default: `[]`.
- `beegfs_conn_interfaces_addr` / `beegfs_conn_interfaces_protocol`: Optional. When either is set, every plain interface name in `beegfs_interfaces` is rewritten as `<name> <addr> <protocol>` (a field left unset is written as `*`) - a structured shortcut for the advanced filter syntax above, for when `beegfs_interfaces` holds plain names (e.g. from NUMA auto-discovery) rather than raw filter-syntax entries. `beegfs_conn_interfaces_addr` is a single IP address; `beegfs_conn_interfaces_protocol` is `4` or `6`. Applies globally - the global `connInterfacesFile`, `connRDMAInterfacesFile`, the metadata service's and every `beegfs_oss` entry's own `connInterfacesFile` - not overridable per `beegfs_oss` entry. Default: unset (interfaces written as plain names, unchanged).
- `beegfs_numa_nic_fallback`: How the NUMA-bound metadata and OSS services use NICs on other NUMA zones. `true`: the NUMA-local NIC(s) come first and the other NIC(s) follow as an HA fallback; the preferred (first) NIC must be NUMA-local. `false`: only NUMA-local NIC(s) are used, with no fallback; every NIC must be NUMA-local, and a service without a local NIC fails the run. Explicit `beegfs_meta_interfaces`/`beegfs_oss[*].interfaces` lists are used as given but validated the same way. To also keep outbound connections off the non-local NIC with `false`, set `beegfs_conn_restrict_outbound_interfaces: true`. Default: `true`.
- `beegfs_conn_auth_beegfs_group`: Whether `/etc/beegfs/conn.auth` is owned by `root:beegfs` with group-read permission (mode `0640`), matching the group the beegfs package's own config files use. When `false`, it's owned by `root:root` with mode `0600` instead - set this to `false` for hosts where the beegfs system group doesn't exist (e.g. beegfs packages not yet installed) or where group access to the auth secret is unwanted. Default: `true`.
- `beegfs_target_id_multiplier`: Multiplier applied to node ID when computing target IDs. Default: `100`.
- `beegfs_node_num_id`: Numeric node ID used for target ID calculation.
- `beegfs_oss`: Dict of object storage server configurations, keyed by port. Each entry:
  - `numa_zone`: Optional. NUMA zone this OSS is local to. Configures `tuneBindToNumaZone` for this OSS - a host can run multiple OSS services bound to different NUMA zones. Also required to auto-discover `devices`/`interfaces` when they're omitted (below). Fails if the resolved devices, or the interfaces `beegfs_numa_nic_fallback` requires to be local, are attached to a different NUMA node.
  - `devices`: Optional. List of block devices for this OSS. If omitted, devices are resolved **label-first**: any device already labeled `ST-<port>-<index>` from a previous run is reused regardless of its current name (device names aren't stable across reboots - see "Reboot-safe device resolution" below), and only genuinely unlabeled slots are filled from fresh discovery (disks matching `beegfs_disk_device_regex` attached to `numa_zone`, excluding the OS disk, `beegfs_meta_dev`, and any device explicitly claimed by another `beegfs_oss` entry) - `numa_zone` is required in that case.
  - `interfaces`: Optional. Overrides `beegfs_interfaces` for this OSS. If omitted and `numa_zone` is set, this is `beegfs_interfaces` reordered so the NIC(s) local to `numa_zone` come first, with or without the others as a fallback (see `beegfs_numa_nic_fallback`) - NUMA-based reordering only works when `beegfs_interfaces` entries are plain interface names, since it looks each one up under `/sys/class/net/`.

  A deployment can configure OSS ports/devices/interfaces statically, rely on NUMA-zone-based auto-discovery, or mix both on the same host.
- `beegfs_disk_device_regex`: Regex matching candidate whole-disk device names eligible for BeeGFS OSS auto-discovery. Only used for `beegfs_oss` entries that omit `devices`. Default: `'^(nvme[0-9]+n[0-9]+|vd[a-z]|sd[a-z])$'`.
- `beegfs_meta_dev`: Optional. Metadata device path (e.g. `/dev/sdb`). If omitted and `beegfs_enable.meta` is true, it's resolved the same label-first way as `beegfs_oss` devices (see below), using `beegfs_meta_dev_label`.
- `beegfs_meta_fstype`: Filesystem of the metadata target. Default: `xfs`. Hosts whose metadata target was formatted with the previous `ext4` default must set `beegfs_meta_fstype: ext4`: an already provisioned disk isn't reformatted (unless `beegfs_force_format`), but it is mounted with this fstype.
- `beegfs_meta_filesystem_opts`: Extra `mkfs` options for the metadata target, placed before `-L <beegfs_meta_dev_label>`. Must match `beegfs_meta_fstype`, e.g. `-i 2048 -I 1024 -J size=400 -O dir_index,filetype` for ext4 or `-K` for xfs. Default: `""` (`mkfs` defaults).
- `beegfs_meta_mount_opts`: Mount options of the metadata target. Default: `noatime,nodiratime,auto`.
- `beegfs_meta_force_format`: Reformat only the metadata device, e.g. to switch it to another `beegfs_meta_fstype`. Stops `beegfs-meta`, unmounts the device, reformats it in place (also when it was resolved from its existing label), mounts it again, reruns `beegfs-setup-meta` and puts the node's previous `registrationToken` back, so mgmtd accepts it again under the same node and target ID (mgmtd rejects a reformatted node with a new token and refuses to delete the node holding the root inode). The node then creates a new, empty root directory. Unlike `beegfs_force_format` it leaves mgmtd, the OSS targets and clients alone. **Destroys all metadata on the host**: without metadata buddy mirroring, the files stored on the file system become unreachable, and their chunks stay on the storage targets as orphans until those are reformatted or cleaned up (e.g. `beegfs-fsck`). Pass it for a single run (`-e beegfs_meta_force_format=true`); it also works with `--tags meta`. Default: `false`.
- `beegfs_meta_tune_bind_to_numa_zone`: Optional. NUMA zone to bind the metadata service to on NUMA systems, since only one metadata device/service is supported per host. Auto-populated when `beegfs_meta_dev` is auto-discovered.
- `beegfs_meta_interfaces`: Optional. Overrides `beegfs_interfaces` for the metadata service. If empty and `beegfs_meta_tune_bind_to_numa_zone` is set, this is `beegfs_interfaces` reordered so the NIC(s) local to that NUMA zone come first, the same way `beegfs_oss[*].interfaces` is derived (plain interface names only, see `beegfs_numa_nic_fallback`). Validated against the NUMA zone like the OSS interfaces. Default: `[]`.
- `beegfs_meta_conn_interfaces_file`: Path of the metadata service's own `connInterfacesFile`, written from the list above and kept separate from the global `/etc/beegfs/connInterfacesFile` used by the client. Default: `/etc/beegfs/beegfs-meta-connInterfacesFile`.
- `beegfs_oss_path_prefix`: Filesystem path prefix for OSS mount points.
- `beegfs_mgmt_grpc_port`: gRPC port of the management service (`grpc-port` in `beegfs-mgmtd.toml`). The alias tasks pass `--mgmtd-addr <beegfs_mgmt_host>:<beegfs_mgmt_grpc_port>` to the `beegfs` CLI, so BeeGFS doesn't need to be mounted on the management host. Default: `8010`.
- `beegfs_license_content`: Content of the BeeGFS license file (obtained from ThinkParQ). Deployed to `/etc/beegfs/license.pem` only on the management node. Leave unset to run without a license. See the [BeeGFS licensing docs](https://doc.beegfs.io/latest/advanced_topics/licensing.html). Note: unsetting this does not remove a previously deployed license file.
- `beegfs_client_mounts`: List of client mounts to configure on this host. Default: `[]`. Each item:
  - `path`: Mount path. Must be unique per mount.
  - `port`: `connClientPort` for this mount. Must be unique per mount.
  - `mgmt_host`: Optional. Overrides `beegfs_mgmt_host` for this mount, for connecting to a different BeeGFS cluster.
  Each mount gets its own `/etc/beegfs/beegfs-client-<port>.conf`.

- `beegfs_client_tune_file_cache_buf_size`: Optional. Sets `tuneFileCacheBufSize` in each client config. Override per mount with `tune_file_cache_buf_size` in `beegfs_client_mounts`. Default: unset (preserves the package setting).

### Reboot-safe device resolution

`/dev/nvmeXnY` names are assigned by asynchronous PCIe probe order and are **not** stable across
reboots. Picking "which disk is meta" / "which disks are OSS target N" fresh every run, purely from
current device names, risks reformatting the wrong physical disk after a renumbering event.

Every disk this role formats gets a durable filesystem label at format time (`beegfs_meta_dev_label`
for meta, `ST-<port>-<index>` per OSS target). Labels live in the on-disk superblock and survive
reboots; `/dev/disk/by-label/<label>` always resolves to whatever device currently holds that
label. `beegfs_meta_dev`/`beegfs_oss[*].devices` auto-discovery checks for an existing label
**first** - fresh NUMA/name-based discovery only ever runs for a slot that was never labeled (first
bootstrap, or a genuinely new disk). The format tasks in `meta.yml`/`oss.yml` skip reformatting any
device that was resolved from an existing label, regardless of its current name, unless
`beegfs_force_format` (or, for the metadata device only, `beegfs_meta_force_format`) is set - which reformats the *label-resolved* device in place, never a
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

### Tags

Device/NUMA discovery and fact building always run; everything else can be selected with `--tags`:

| Tag | Runs | Restarts / reloads |
|---|---|---|
| `mgmt`, `mon`, `meta`, `oss`, `client` | everything for that service (config, format/mount, setup) | that service |
| `fs` | OSS format and mount | - |
| `meta_config` | metadata server tunings (`beegfs_meta_tune_*`, ...) | meta |
| `oss_config` | storage server tunings (`beegfs_oss_tune_*`, `tuneBindToNumaZone`, ...) | storage, all ports |
| `client_config` | client tunings and `quotaEnabled` | client remount, see below |
| `interfaces` | every `connInterfacesFile` (global, meta, per OSS port) and the NIC NUMA checks | matching services |
| `tuning` | sysctls and the `beegfs-oss-tuning` device tuning service | tuning service |
| `sysctl` | only the sysctls | - (applied directly) |
| `install`, `repos`, `rdma`, `alias` | packages, repo, RDMA packages, aliases on mgmt | - |

BeeGFS reads a client's config only at mount time. Set `beegfs_client_remount_on_change: true` to have
changed client config (`client`, `client_config`, `config`, `interfaces`) unmount and mount again; this fails while
processes still hold the mount. Restart handlers act on every selected host at once, so use `--limit` to
try a change on a single node first, e.g.:

```sh
ansible-playbook beegfs.yml --tags oss_config --limit oss01 -e beegfs_oss_tune_num_workers=24
```

The role must be pulled in so that its own tags decide: a static `roles:`/`import_role`, or an
`include_role` tagged `always`. An untagged `include_role` is skipped entirely under `--tags`, and `apply`
would give every task the same tags.

### Deploying many nodes in parallel

The role is written to run on every BeeGFS node of a play at the same time: per-port and per-device
work loops inside a task rather than looping `include_tasks`, so the default `linear` strategy keeps all
hosts in step. Ansible itself only talks to `forks` hosts at once (5 by default), so set it to at least
the number of BeeGFS nodes, and enable pipelining, e.g. in `ansible.cfg`:

```ini
[defaults]
forks = 50

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

Formatting new NVMe devices can spend most of its time discarding blocks. If the devices are new or
already trimmed, adding `-K` to `beegfs_filesystem_opts` (and `beegfs_meta_filesystem_opts`) skips that
for XFS.

To see where time is spent, enable the `ansible.posix.profile_tasks` and `ansible.posix.timer`
callbacks (`ANSIBLE_CALLBACKS_ENABLED=ansible.posix.profile_tasks,ansible.posix.timer`).
