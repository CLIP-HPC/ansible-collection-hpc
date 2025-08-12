# clip.hpc.multirole Role

This role configures Multi-Homing/Rail via NetworkManager


## Role Variables

- `multirail_interfaces`: Required. The names of the 2 interfaces which shoukd be configured for multirail setup


## Example Playbook


Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

```yaml
- name: Execute tasks on servers
  hosts: servers
  roles:
    - role: clip.hpc.multirail
      multirail_interfaces: [eth0,eth1]
```

Another way to consume this role would be:

```yaml
- name: Initialize the run role from clip.hpc
  hosts: servers
  gather_facts: false
  tasks:
    - name: Trigger invocation of run role
      ansible.builtin.include_role:
        name: clip.hpc.multirail
      vars:
        multirail_interfaces: [eth0,eth1]
```
