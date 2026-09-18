# clip.hpc.rocev2 Role

This role configured NVIDIA NIC firmwware swettings to trust DSCP and configure TOS 104 to use for RDMA traffic


## Role Variables

| Variable                    | Default   | Description                                                                                                                                       |
|------------------------------|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `rocev2_mlx_qos_service_state` | `started` | State of the `mlnx-roce-qos` service.                                                                                                             |
| `rocev2_ethtool_ring_rx`      | unset     | Desired `ethtool.ring-rx` value applied to the NetworkManager connection of every discovered RoCE NIC (`/sys/class/infiniband/mlx5_*`): an integer ring size, or an empty string (`""`) to remove an existing override. Left unset (the default), the role does not touch ring-rx at all. |
| `rocev2_ethtool_ring_tx`      | unset     | Desired `ethtool.ring-tx` value applied to the NetworkManager connection of every discovered RoCE NIC (`/sys/class/infiniband/mlx5_*`): an integer ring size, or an empty string (`""`) to remove an existing override. Left unset (the default), the role does not touch ring-tx at all. |

When either value is set (including to an empty string), the role only touches RoCE NICs that are
currently active/up, and only modifies connections whose current setting differs from the desired
value. NetworkManager cannot hot-reapply the `ethtool` setting, so an integer value is applied live
with `ethtool -G` (no link flap); the NetworkManager connection profile is updated in the same run,
so the value is reasserted correctly on the next reconnect or reboot.

Setting either variable to `""` removes NetworkManager's override instead of applying a specific
size (`ethtool.ring-rx`/`ring-tx` back to NetworkManager's own `-1` "unmanaged" default) — and, per
the same idempotency check as any other value, this only runs the removal command when the profile
currently has an override set; if it's already unmanaged, nothing changes. This is **not**
live-applied — the driver's own default ring size only takes effect the next time the interface
reconnects or the host reboots, since that's when NetworkManager stops re-asserting a value it no
longer manages.

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
