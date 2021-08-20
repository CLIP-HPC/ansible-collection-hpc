# Ansible Collection: vbc.linux

This repo hosts the `vbc.linux` Ansible Collection.

The collection includes the roles to do baseline configuration of Linux hosts.

## Installation and Usage

Before using the `vbc.linux` collection, you need to install the collection with the `ansible-galaxy` CLI:

`ansible-galaxy collection install vbc.linux`

You can also include it in a `requirements.yml` file and install it through `ansible-galaxy collection install -r requirements.yml` using the format:

```yaml
collections:
- name: vbc.linux
```

## Roles

Following roles are supported:

- [certificate](roles/certificate): Install & configure host certificates
- [container](roles/container): Install & configure podman for containers
- [dns](roles/dns): Configure DNS records in infoblox
- [firewalld](roles/firewalld): Install & configure firewalld
- [ntp](roles/ntp): Install & configure NTP service
- [promtail](roles/promtail): Install & configure promtail agent
- [sssd](roles/sssd): Install & configure SSSD (active directory)
- [sudoers](roles/sudoers): Configure sudoers list
- [syslog](roles/syslog): Install & configure syslog
- [user](roles/user): Configure user on host
