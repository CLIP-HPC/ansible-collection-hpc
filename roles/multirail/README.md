# clip.hpc.multirail Role

This role configures multi-homing/multi-rail source routing for two interfaces via NetworkManager, so
traffic from an interface's address always leaves through that interface.

For each interface (in list order) the role:

- adds a routing table (`201`, `202`, named after the interface in `/etc/iproute2/rt_tables.d/multirail.conf`)
  with a route for each of the interface's subnets and a default route via the interface's gateway, for
  IPv4 and, when the interface has a global IPv6 address, for IPv6
- adds a routing rule (priority `201`/`202`) for every IPv4 address (primary and secondary) and every
  global IPv6 address of the interface that sends traffic from that address to the interface's table
- keeps the default route in the main routing table on the first interface only (`ipv4.never-default`
  on the second)
- sets the ARP, reverse path filter and `accept_local` sysctls for `all`, `default` and each interface in
  `/etc/sysctl.d/99-multirail-ipv4.conf`
- checks that traffic from each interface's IPv4 address is routed out of that interface (`multirail_verify`)

The routes and rules are built from the gathered facts, so facts (at least the `network` subset) must be
gathered before the role runs. When the NetworkManager connections change, the routes, routing rules and
`ipv4.never-default` of the profiles are applied to the active connections with `nmcli device modify`. Unlike
`nmcli device reapply`, this doesn't fail when the profile has other changes that can't be reapplied, such as
the ethtool ring sizes set by `clip.hpc.rocev2`, and leaves them pending.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `multirail_interfaces` | required | The two interfaces to configure. The first one keeps the default route in the main routing table. |
| `multirail_ipv4_gateways` | `{}` | IPv4 gateway per interface name for the default route in that interface's table, e.g. `{eth1: 10.0.2.254}`. Interfaces without an entry use the first usable address of their primary IPv4 subnet. |
| `multirail_net_arp_ignore` | `2` | `arp_ignore`: only answer ARP for addresses on the receiving interface and from senders in the same subnet. |
| `multirail_net_arp_announce` | `2` | `arp_announce`: always use the outgoing interface's address as ARP source. |
| `multirail_net_arp_filter` | `1` | `arp_filter`: only answer ARP on the interface the reply would be routed through. |
| `multirail_net_rp_filter` | `2` | `rp_filter`: `2` (loose) drops packets from unroutable sources but accepts packets that arrive on a different rail than the reply would use. `1` (strict) drops them. |
| `multirail_net_accept_local` | `1` | `accept_local`: accept packets with a local source address, needed for traffic between the rails of the same host. |
| `multirail_nmcli_connection_prefix` | `cloud-init` on EL10, `System` otherwise | Prefix of the NetworkManager connection names (`<prefix> <interface>`). |
| `multirail_verify` | `true` | Check the resulting routing with `ip route get` after applying the changes. Flushes the play's pending handlers first. |

The sysctls are also set per interface because the kernel uses the higher of the `all` and the
per-interface value for `arp_ignore`, `arp_announce` and `rp_filter`: setting `all` alone can't lower a
value an interface already has.

IPv6 global addresses are taken as gathered. If IPv6 privacy (temporary) addresses are enabled on the
interfaces, the rules change whenever the temporary address does.

## Example Playbook

```yaml
- name: Configure multirail on servers
  hosts: servers
  roles:
    - role: clip.hpc.multirail
      multirail_interfaces: [eth0, eth1]
```

Another way to consume this role would be:

```yaml
- name: Configure multirail on servers
  hosts: servers
  tasks:
    - name: Configure multirail
      ansible.builtin.include_role:
        name: clip.hpc.multirail
      vars:
        multirail_interfaces: [eth0, eth1]
        multirail_ipv4_gateways:
          eth1: 10.0.2.254
```

## Verification

```bash
ip rule show                                  # priority 201/202 rules per address
ip route show table 201                       # subnet route(s) + default route
ip route get 192.0.2.1 from <eth1 address>    # dev eth1 table eth1
sysctl net.ipv4.conf.eth1.rp_filter           # 2
```
