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
- `dell_dsu_install`: Install DSU before use. Default: `true`.
- `dell_dsu_version` / `dell_dsu_rpm_url`: The `dell-system-update` RPM is installed directly from Dell's URL (default `https://linux.dell.com/repo/hardware/dsu/os_independent/x86_64/dell-system-update-<version>.x86_64.rpm`); the Dell repositories themselves are configured by `bootstrap.cgi`. Dell only keeps the latest RPM there, so the pinned version eventually 404s - bump `dell_dsu_version` or override the URL. Default version: `2.3.0.1-26.08.00`.
- `dell_dsu_rpm_disable_gpg_check`: Skip RPM signature verification for that install (Dell's key is only imported by the bootstrap). Default: `true`.
- `dell_dsu_binary`: Path of the `dsu` binary. Default: `/usr/sbin/dsu`.
- `dell_dsu_run_postinstall` / `dell_dsu_postinstall_marker`: The `dell-system-update` RPM `%post` scriptlet can fail inside the transaction, which leaves DSU unable to run ("Shared library integrity check failed"). This workaround re-runs its steps as tasks (remove `/etc/ld.so.conf.d/dsulib.conf`, `ldconfig`, `chmod +x getOEMSystemId`, then download and run Dell's `bootstrap.cgi`), once per host when the package changed or the marker file is missing. Skipped when running from a live ISO. Default: `true`.
- `dell_dsu_bootstrap_url` / `dell_dsu_bootstrap_dest`: Where the bootstrap script is fetched from and saved to. It is downloaded over HTTPS and run as root without a checksum, exactly like the RPM scriptlet does.
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

- "Updates available" is decided by `dsu --preview` return code 34 ("No Applicable Updates Found"); any other accepted code counts as updates available.
- DSU return codes 25 and 26 (partial failure / partial failure and reboot required) mean some updates were applied: the role still reboots when requested, and then fails the host.
- If `dsu --inventory` fails because DSU cannot verify its libraries (return code 40, or "integrity check failed"), the role stops with a hint to check the post-install bootstrap. This is the check that the bootstrap workaround worked.
- Dell's guide suggests rebooting the iDRAC and retrying when DSU intermittently fails to apply updates; the role does not do this.
