# clip.hpc.smartctl_exporter Role

Installs and configures the [Prometheus smartctl_exporter](https://github.com/prometheus-community/smartctl_exporter), which exposes S.M.A.R.T. disk health metrics collected via `smartctl` for scraping.

The role downloads the official release archive from GitHub, verifies it against the upstream `sha256sums.txt`, installs the `smartctl_exporter` binary, and manages it as a systemd service. The `smartmontools` package (providing `smartctl`) is installed by default.

## Role Variables

- `smartctl_exporter_version`: Version of smartctl_exporter to install (without the leading `v`). Default: `0.14.0`.
- `smartctl_exporter_arch_map`: Maps `ansible_architecture` to the arch suffix used in upstream release asset names. Default: `{x86_64: amd64, aarch64: arm64}`.
- `smartctl_exporter_arch`: Release arch suffix to download. Derived from `smartctl_exporter_arch_map` by default.
- `smartctl_exporter_download_url`: URL of the release archive. Derived from `smartctl_exporter_version`/`smartctl_exporter_arch` by default.
- `smartctl_exporter_checksum_url`: URL of the upstream `sha256sums.txt`, used to verify the downloaded archive.
- `smartctl_exporter_checksum_verify`: Whether to verify the download against `smartctl_exporter_checksum_url`. Default: `true`.
- `smartctl_exporter_download_dir`: Directory used to cache the downloaded archive and its extracted contents. Default: `/usr/local/src/smartctl_exporter`.
- `smartctl_exporter_binary_install_dir`: Directory the `smartctl_exporter` binary is installed into. Default: `/usr/local/bin`.
- `smartctl_exporter_install_smartmontools`: Whether to install the `smartmontools` package. Default: `true`.
- `smartctl_exporter_user` / `smartctl_exporter_group`: User/group the service runs as. Default: `root`. smartctl needs root on most kernels to issue the `ATA_12`/`ATA_16` passthrough commands used to query SATA/USB-bridged devices - this matches the [upstream systemd unit](https://github.com/prometheus-community/smartctl_exporter/blob/master/systemd/smartctl_exporter.service). The role does not grant any Linux capabilities on your behalf, so if you override these to a non-root account you must separately grant it `CAP_SYS_RAWIO`/`CAP_SYS_ADMIN` (e.g. `AmbientCapabilities=` in a systemd drop-in, or `setcap` on the installed binary) and validate it against your actual kernel/device/USB-bridge mix - some devices still require full root regardless of capabilities.
- `smartctl_exporter_smartctl_path`: Path to `smartctl` on the target host. Default: `/usr/sbin/smartctl`.
- `smartctl_exporter_smartctl_interval`: Polling interval (`--smartctl.interval`). Default: `60s`.
- `smartctl_exporter_devices`: Explicit list of devices to monitor (`--smartctl.device`, repeatable). Auto-scans all devices when empty. Default: `[]`.
- `smartctl_exporter_device_include` / `smartctl_exporter_device_exclude`: Regexes to include/exclude devices from auto-scan. Default: `""`.
- `smartctl_exporter_port`: TCP port the exporter listens on. Default: `9633`.
- `smartctl_exporter_web_listen_address`: Value passed to `--web.listen-address`. Default: `":{{ smartctl_exporter_port }}"`.
- `smartctl_exporter_web_telemetry_path`: Value passed to `--web.telemetry-path`. Default: `/metrics`.
- `smartctl_exporter_web_config_file`: Optional path to an exporter-toolkit web config file for TLS/basic auth (`--web.config.file`). Default: `""` (disabled) - like most Prometheus exporters, the metrics endpoint is unauthenticated and unencrypted unless this is set, so rely on network segmentation (or set this) to control who can scrape it.
- `smartctl_exporter_log_level` / `smartctl_exporter_log_format`: Passed to `--log.level`/`--log.format`. Defaults: `info` / `logfmt`.
- `smartctl_exporter_extra_args`: Additional raw CLI arguments appended to the `ExecStart` line. Default: `[]`.
- `smartctl_exporter_service_enabled` / `smartctl_exporter_service_state`: systemd enablement/state for the service. Defaults: `true` / `started`.
- `smartctl_exporter_manage_firewalld`: Whether to open `smartctl_exporter_port` in firewalld. Default: `false`.
- `smartctl_exporter_firewalld_zone`: firewalld zone the port is opened in when `smartctl_exporter_manage_firewalld` is true. Default: `public`.

## Example Playbook

```yaml
- name: Install the smartctl exporter
  hosts: storage_servers
  roles:
    - role: clip.hpc.smartctl_exporter
      vars:
        smartctl_exporter_device_exclude: '^/dev/sd[a-c]$'
        smartctl_exporter_manage_firewalld: true
```
