# clip.hpc.doca Role

Install [NVIDIA DOCA](https://docs.nvidia.com/doca/sdk/index.html).

This role configured NVIDIA DOCA driver for the NVIDIA/Mellanox NICs

## Role Variables

- `doca_version`: Optional. String giving doca version. Default 3.0.0
- `doca_profile`: Optional. Name of [profile](https://docs.nvidia.com/doca/sdk/nvidia+doca+profiles/index.html) defining subset of DOCA to install. Default is `doca-ofed`.
- `doca_repo_url`: Optional. URL of DOCA repository. Default is appropriate upstream public repository for DOCA version, distro version and architecture.
- `doca_use_upstream_repo`: Optional. Whether to configure the upstream DOCA repositories or assume that they are avaialble through other means (pulp, Satellite). Default: true
- `doca_reboot`: Optional. Reboot the host right after the DOCA packages are installed, so the new drivers are loaded. Default: `false`.

## Reboot

When the role installs the DOCA packages, it sets the fact `doca_reboot_required` to `true`
(`false` otherwise) and prints that a reboot is needed, also in check mode. With `doca_reboot: false`
(the default), it adds the line `clip.hpc.doca: DOCA packages installed` to `/run/reboot-required`
and doesn't reboot: reboot the host through your own path, such as `scontrol reboot ASAP` for a
Slurm node or one storage server at a time. With `doca_reboot: true`, it reboots the host right
away. `/run/reboot-required` stays until the host reboots.


## Example Playbook


Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

```yaml
- name: Execute tasks on servers
  hosts: servers
  roles:
    - role: clip.hpc.docs
      doca_version: 3.0.0
```

Another way to consume this role would be:

```yaml
- name: Initialize the run role from clip.hpc
  hosts: servers
  gather_facts: false
  tasks:
    - name: Trigger invocation of run role
      ansible.builtin.include_role:
        name: clip.hpc.docs
      vars:
        doca_version: 3.0.0
```
