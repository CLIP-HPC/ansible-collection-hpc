# clip.hpc.rocev2 Role

This role configured NVIDIA NIC firmwware swettings to trust DSCP and configure TOS 106 to use for RDMA traffic


## Example Playbook


Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

```yaml
- name: Execute tasks on servers
  hosts: servers
  roles:
    - role: clip.hpc.rocev2
```

Another way to consume this role would be:

```yaml
- name: Initialize the run role from clip.hpc
  hosts: servers
  gather_facts: false
  tasks:
    - name: Trigger invocation of run role
      ansible.builtin.include_role:
        name: clip.hpc.rocev2
```
