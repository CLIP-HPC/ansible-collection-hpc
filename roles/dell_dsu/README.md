# clip.hpc.dell_dsu Role

Installs [Dell System Update (DSU)](https://www.dell.com/support/manuals/en-us/system-update), inventories and previews available firmware/driver/BIOS updates on Dell servers, and optionally applies them in-band from the host OS.

By default the role is a **dry run**: it installs DSU, collects `dsu --inventory` and `dsu --preview`, and exposes the results as facts. Updates are only applied with `dell_dsu_apply: true`, and hosts are only rebooted with `dell_dsu_reboot: true`. Hosts that are not Dell hardware (`system_vendor`) are skipped unless `dell_dsu_force` is set.

This role does not touch the scheduler. Drain nodes (e.g. in Slurm) before applying updates, and use `serial:` when rolling across a cluster.

## Role Variables

- `dell_dsu_force`: Run on hosts not detected as Dell hardware. Default: `false`.
- `dell_dsu_apply`: Apply updates (otherwise inventory and preview only). Default: `false`.
- `dell_dsu_apply_downgrades`: Also pass `--apply-downgrades`. Default: `false`.
- `dell_dsu_reboot`: Reboot when DSU reports a reboot is required (return code 8). Default: `false`.
- `dell_dsu_reboot_timeout`: Seconds to wait for the host after reboot. Default: `1800`.
- `dell_dsu_apply_timeout` / `dell_dsu_apply_poll_interval`: `dsu --apply-upgrades` runs in the background (async) and is polled, so a dropped SSH connection neither kills the update nor fails the host. Maximum run time in seconds (the job is killed after this) and polling interval. Default: `3600` / `30`.
- `dell_dsu_wait_timeout`: Before any DSU command, the role waits up to this many seconds for an already running `dsu` process (for example from an earlier run that lost its connection) instead of failing with "DSU already in use!". Default: `3600`.
- `dell_dsu_install`: Install DSU before use. Default: `true`.
- `dell_dsu_package`: Package installed from the repositories configured by the bootstrap script, only when it is not installed yet (initial bootstrapping); an installed DSU is never upgraded or reinstalled by the role. Default: `dell-system-update`.
- `dell_dsu_binary`: Path of the `dsu` binary. Default: `/usr/sbin/dsu`.
- `dell_dsu_run_bootstrap` / `dell_dsu_bootstrap_marker`: The role downloads and runs Dell's `bootstrap.cgi` (with `y` fed to its prompts), which configures the DSU yum repositories and GPG keys, and then installs the package from them. This replaces the `dell-system-update` RPM `%post` scriptlet, which runs the same script but fails inside the RPM transaction and leaves DSU unable to run ("Shared library integrity check failed"). It runs once per host, when the marker file is missing or the package is not installed. Default: `true`.
- `dell_dsu_bootstrap_url`: Where the bootstrap script is fetched from. It is downloaded to a temporary file (removed afterwards), over HTTPS, and run as root without a checksum, exactly like the RPM scriptlet does.
- `dell_dsu_catalog_location`: Optional catalog (`.xml`, `.gz`, `.cab`) passed as `--catalog-location`. Default: `""`.
- `dell_dsu_component_types`: Restrict to component types (`--component-type`), e.g. `[FRMW, BIOS]`. Default: `[]` (all).
- `dell_dsu_extra_args`: Extra raw DSU arguments. Default: `[]`.
- `dell_dsu_ok_return_codes`: DSU return codes not treated as failure. Default: `[0, 8, 34]`.
- `dell_dsu_inventory_non_interactive`: Also pass `--non-interactive` to `dsu --inventory`. Set to `false` if your DSU version rejects the combination (return code 6). Default: `true`.
- `dell_dsu_clear_stale_lock` / `dell_dsu_lock_file`: DSU prints "DSU already in use!" when a killed run leaves its lock file behind. The role removes the file only when no `dsu` process is running. Dell's guide spells the path `/temp/DSUINACTION.txt`; the default `/tmp/DSUINACTION.txt` is unverified, so check it on a node. Default: `true` / `/tmp/DSUINACTION.txt`.

## Facts set

`dell_dsu_is_dell`, `dell_dsu_inventory_output`, `dell_dsu_preview_output`, `dell_dsu_preview_rc`, `dell_dsu_updates_available`, and (when applying) `dell_dsu_update_rc`, `dell_dsu_update_output`, `dell_dsu_update_partial`, `dell_dsu_reboot_required`.

## Playbooks

Two standalone playbooks ship in `playbooks/`:

- `clip.hpc.dell_dsu_report`: inventories every Dell node and reports which have updates available. Variables: `dell_dsu_hosts` (default `all`), `dell_dsu_report_dest` (optional JSON file on the controller).
- `clip.hpc.dell_dsu_update`: applies updates. Variables: `dell_dsu_hosts` (default `all`), `dell_dsu_serial` (default `1`), `dell_dsu_reboot` (default `false`), plus any role variable.

```shell
ansible-playbook clip.hpc.dell_dsu_report -e dell_dsu_hosts=compute -e dell_dsu_report_dest=./dsu.json
ansible-playbook clip.hpc.dell_dsu_update -e dell_dsu_hosts=node01 -e dell_dsu_reboot=true
```

## Notes

- If the connection is lost for longer than the polling retries allow, the host fails but DSU keeps running on the node; re-running the play waits for it to finish and then re-previews what is left. The inventory and preview commands are short and are not retried.
- "Updates available" is decided by `dsu --preview` return code 34 ("No Applicable Updates Found"); any other accepted code counts as updates available.
- DSU return codes 25 and 26 (partial failure / partial failure and reboot required) mean some updates were applied: the role still reboots when requested, and then fails the host.
- If `dsu --inventory` fails because DSU cannot verify its libraries (return code 40, or "integrity check failed"), the role stops with a hint to check the bootstrap. This is also the check that the bootstrap worked.
- Dell's guide suggests rebooting the iDRAC and retrying when DSU intermittently fails to apply updates; the role does not do this.
