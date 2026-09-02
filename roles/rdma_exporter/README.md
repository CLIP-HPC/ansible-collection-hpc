# clip.hpc.rdma_exporter Role

Installs and configures the [Prometheus rdma_exporter](https://github.com/yuuki/rdma_exporter), which exposes RDMA (InfiniBand/RoCE) NIC statistics collected from Linux sysfs and RDMA netlink for scraping.

The role downloads the official release archive from GitHub, verifies it against the upstream `rdma_exporter_checksums.txt`, and installs the `rdma_exporter` binary. The `rdma_exporter.service` systemd unit itself, and (optionally) the hardware-counter enablement stack below, are fetched **verbatim from the upstream repository's [`deploy/`](https://github.com/yuuki/rdma_exporter/tree/main/deploy) directory**, pinned to the `v{{ rdma_exporter_version }}` tag, rather than reimplemented locally - this keeps the role from drifting out of sync with upstream's own deployment story. Exporter configuration is passed via an `EnvironmentFile` (`/etc/rdma_exporter.env`), matching the deployment style of that same upstream unit.

## Role Variables

- `rdma_exporter_version`: Version of rdma_exporter to install (without the leading `v`). Also used as the git tag (`v{{ rdma_exporter_version }}`) that `deploy/` assets are fetched from. Default: `0.7.3`.
- `rdma_exporter_arch_map`: Maps `ansible_architecture` to the arch suffix used in upstream release asset names. Default: `{x86_64: amd64, aarch64: arm64}`.
- `rdma_exporter_arch`: Release arch suffix to download. Derived from `rdma_exporter_arch_map` by default.
- `rdma_exporter_download_url`: URL of the release archive. Derived from `rdma_exporter_version`/`rdma_exporter_arch` by default.
- `rdma_exporter_checksum_url`: URL of the upstream `rdma_exporter_checksums.txt`, used to verify the downloaded archive.
- `rdma_exporter_checksum_verify`: Whether to verify the download against `rdma_exporter_checksum_url`. Default: `true`.
- `rdma_exporter_download_dir`: Directory used to cache the downloaded archive and its extracted contents. Default: `/usr/local/src/rdma_exporter`.
- `rdma_exporter_binary_install_dir`: Directory the `rdma_exporter` binary is installed into. **Must stay `/usr/local/bin`**: the fetched `rdma_exporter.service` unit hardcodes this path in `ExecStart`; the role asserts this before installing. Default: `/usr/local/bin`.
- `rdma_exporter_deploy_ref`: Git ref used to fetch `deploy/` assets from upstream. Default: `"v{{ rdma_exporter_version }}"`.
- `rdma_exporter_deploy_raw_base_url`: Base URL `deploy/` assets are fetched from (`raw.githubusercontent.com`), pinned to `rdma_exporter_deploy_ref`.
- `rdma_exporter_systemd_unit_url`: URL of [`deploy/systemd/rdma_exporter.service`](https://github.com/yuuki/rdma_exporter/blob/main/deploy/systemd/rdma_exporter.service), fetched verbatim to `/etc/systemd/system/rdma_exporter.service`.
- `rdma_exporter_user` / `rdma_exporter_group`: User/group the service runs as. **Must stay `rdma_exporter`**: the fetched upstream unit hardcodes this identity; the role asserts this before installing. It is a dedicated, unprivileged system account - reading RDMA sysfs counters and issuing RDMA netlink GET requests does not require any Linux capability, so the shipped unit runs with an empty `AmbientCapabilities`/`CapabilityBoundingSet`. Default: `rdma_exporter`.
- `rdma_exporter_port`: TCP port the exporter listens on. Default: `9879`.
- `rdma_exporter_listen_address`: Value passed via `RDMA_EXPORTER_LISTEN_ADDRESS`. Default: `":{{ rdma_exporter_port }}"`.
- `rdma_exporter_metrics_path`: Value passed via `RDMA_EXPORTER_METRICS_PATH`. Default: `/metrics`.
- `rdma_exporter_health_path`: Value passed via `RDMA_EXPORTER_HEALTH_PATH`. Default: `/healthz`.
- `rdma_exporter_log_level`: Value passed via `RDMA_EXPORTER_LOG_LEVEL` (`debug`, `info`, `warn`, `error`). Default: `info`.
- `rdma_exporter_sysfs_root`: Root directory used to read RDMA sysfs data (`RDMA_EXPORTER_SYSFS_ROOT`). Default: `/sys`.
- `rdma_exporter_scrape_timeout`: Upper bound for metric gathering per scrape (`RDMA_EXPORTER_SCRAPE_TIMEOUT`). Default: `5s`.
- `rdma_exporter_collector_ethtool`: Whether to collect RoCEv2 PFC and netdev hardware ethtool families (buffer/PCIe/PHY, IEEE 802.3x pause, pause storm, vport RDMA). Default: `true`.
- `rdma_exporter_collector_optional_counters`: Whether to collect optional mlx5 hardware counters (`cc_*`, `rdma_{rx,tx}_{bytes,packets}`) via RDMA netlink. The exporter never enables these counters itself - see [Enabling optional/QP hardware counters](#enabling-optionalqp-hardware-counters) below. Default: `true`.
- `rdma_exporter_collector_qp_counters`: Whether to collect live auto-type QP hardware counters via a separate RDMA netlink socket. Off by default: the dump can exceed the scrape timeout on dense hosts. Default: `false`.
- `rdma_exporter_exclude_devices`: List of RDMA devices to exclude from collection (`RDMA_EXPORTER_EXCLUDE_DEVICES`), useful to avoid kernel log flooding on firmware-restricted devices (NVIDIA DGX, Umbriel, GB200 systems). Default: `[]`.
- `rdma_exporter_extra_environment`: Additional key/value pairs appended to the `rdma_exporter` `EnvironmentFile`. Default: `{}`.
- `rdma_exporter_service_enabled` / `rdma_exporter_service_state`: systemd enablement/state for the service. Defaults: `true` / `started`.
- `rdma_exporter_manage_firewalld`: Whether to open `rdma_exporter_port` in firewalld. Default: `false`.
- `rdma_exporter_firewalld_zone`: firewalld zone the port is opened in when `rdma_exporter_manage_firewalld` is true. Default: `public`.
- `rdma_exporter_manage_hardware_counters`: Whether to fetch and enable the upstream hardware-counter enablement stack. See [Enabling optional/QP hardware counters](#enabling-optionalqp-hardware-counters) below. Default: `false`.
- `rdma_exporter_hw_counters_script_url` / `rdma_exporter_hw_counters_service_url` / `rdma_exporter_hw_counters_udev_rule_url`: URLs of [`deploy/scripts/rdma-enable-hardware-counters.sh`](https://github.com/yuuki/rdma_exporter/blob/main/deploy/scripts/rdma-enable-hardware-counters.sh), [`deploy/systemd/rdma-hardware-counters.service`](https://github.com/yuuki/rdma_exporter/blob/main/deploy/systemd/rdma-hardware-counters.service) and [`deploy/udev/90-rdma-hardware-counters.rules`](https://github.com/yuuki/rdma_exporter/blob/main/deploy/udev/90-rdma-hardware-counters.rules), fetched verbatim.
- `rdma_exporter_hw_counters_optional_counters`: Optional counter names passed to `rdma statistic set ... optional-counters`. Empty defers to the script's own built-in default (`cc_rx_ce_pkts,cc_rx_cnp_pkts,cc_tx_cnp_pkts`). Default: `[]`.
- `rdma_exporter_hw_counters_enable_qp_counters`: Also enable QP auto-type + optional-counters on, feeding `rdma_exporter_collector_qp_counters`. Default: `false`.

## Example Playbook

```yaml
- name: Install the RDMA exporter
  hosts: infiniband_nodes
  roles:
    - role: clip.hpc.rdma_exporter
      vars:
        rdma_exporter_exclude_devices: ['mlx5_0', 'mlx5_1']
        rdma_exporter_collector_qp_counters: true
        rdma_exporter_manage_firewalld: true
```

## Enabling optional/QP hardware counters

`rdma_exporter_collector_optional_counters` and `rdma_exporter_collector_qp_counters` only scrape counters that are already enabled in the kernel; the exporter never calls `rdma statistic set` or binds QPs itself. Enabling the underlying mlx5 optional (`cc_*`) or auto-type QP counters is a separate, host-level, `CAP_NET_ADMIN` administrative step, and enablement is **not persistent** across reboot, driver reload, or VF hotplug - see upstream's [Run](https://github.com/yuuki/rdma_exporter#run) section.

Setting `rdma_exporter_manage_hardware_counters: true` has the role fetch and wire up upstream's own re-enablement tooling, pinned to `v{{ rdma_exporter_version }}`:

- [`deploy/scripts/rdma-enable-hardware-counters.sh`](https://github.com/yuuki/rdma_exporter/blob/main/deploy/scripts/rdma-enable-hardware-counters.sh) → `/usr/local/sbin/rdma-enable-hardware-counters`, a root oneshot that runs `rdma statistic set` (and, with `rdma_exporter_hw_counters_enable_qp_counters: true`, `rdma statistic qp set link ... auto type on optional-counters on`) against every port that advertises optional counters.
- [`deploy/systemd/rdma-hardware-counters.service`](https://github.com/yuuki/rdma_exporter/blob/main/deploy/systemd/rdma-hardware-counters.service) → `/etc/systemd/system/rdma-hardware-counters.service`, enabled (not started) so it fires on the next InfiniBand hotplug event.
- [`deploy/udev/90-rdma-hardware-counters.rules`](https://github.com/yuuki/rdma_exporter/blob/main/deploy/udev/90-rdma-hardware-counters.rules) → `/etc/udev/rules.d/90-rdma-hardware-counters.rules`, which triggers the service via `SYSTEMD_WANTS` on `ACTION=="add", SUBSYSTEM=="infiniband"`. When this rule changes, the role reloads udev rules and re-triggers existing InfiniBand devices so already-present hardware doesn't have to wait for a reboot or hotplug.
- `/etc/rdma-hardware-counters.env`, role-managed from `rdma_exporter_hw_counters_optional_counters` / `rdma_exporter_hw_counters_enable_qp_counters`.

Enabling optional counters allocates mlx5 flow counters and steering rules and **may affect datapath performance** - measure before leaving them on fleet-wide. This is off by default; confirm with `rdma statistic mode` on a target host before trusting `/metrics`.

Setting `rdma_exporter_manage_hardware_counters` back to `false` (its default) reverses this: the role stops and disables `rdma-hardware-counters.service`, then removes the script, unit, udev rule and env file, and reloads udev/systemd so the host stops re-enabling hardware counters on future hotplug events. It does not itself run `rdma statistic set ... optional-counters ""` to clear any already-enabled counter state on live ports - that would need an explicit operator action (or a reboot/driver reload, since enablement isn't persistent anyway).
