# clip.hpc.lldp Role

This role installs and enables the `lldpd` service so the host transmits LLDP
frames the switch can use to learn about it, and enables LLDP RX reporting on
NetworkManager connection profiles so the host can see switch-side neighbor
information (e.g. via `nmcli device lldp list`). By default this is enabled
on every non-loopback interface with an active NetworkManager connection; set
`lldp_interfaces` to restrict it to specific interfaces instead.

`community.general.nmcli` has no dedicated parameter for NetworkManager's
`connection.lldp` property, so that part is implemented with raw `nmcli`
commands.

## Role Variables

- `lldp_interfaces`: Optional. Interface names whose NetworkManager connection
  profile should have LLDP RX reporting enabled. Default: `[]`, which enables
  it on every non-loopback interface that currently has an active
  NetworkManager connection.
- `lldp_package_state`: Optional. State for the `lldpd` package. Default:
  `present`.
- `lldp_service_state`: Optional. State for the `lldpd` service. Default:
  `started`.

## Example Playbook

```yaml
- name: Execute tasks on servers
  hosts: servers
  roles:
    - role: clip.hpc.lldp
      lldp_interfaces: [eth0, eth1]
```

Another way to consume this role would be:

```yaml
- name: Initialize the run role from clip.hpc
  hosts: servers
  tasks:
    - name: Trigger invocation of run role
      ansible.builtin.include_role:
        name: clip.hpc.lldp
      vars:
        lldp_interfaces: [eth0, eth1]
```
