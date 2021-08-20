Role Name
=========

Role:
* installs and enables firewalld service
* assigns interfaces, services and ports  to zones

TO DO:
* source based zones, variable layout is prepared, tasks for this should be relatively straightforward

Requirements
------------

none.

Role Variables
--------------

Role uses following variables.

```
---
# defaults file for role-firewalld
################################################################################
role_firewalld_present: true
role_firewalld_default_zone: "public"
################################################################################
# list of interface based zones,
#   if 'ifname' is not explicitly specified, role will use the default ansible_default_ipv4.interface
#   if zone is not explicitly specified, role will use the role_firewalld_default_zone
################################################################################
role_firewalld_interfaces:
  - ifname:
    zone:
    services:
      - "ssh"
    ports:
      - "9999/tcp"
################################################################################
# source based zones, all three parameters MUST be specified explicitly
# NOT IMPLEMENTED CURRENTLY
################################################################################
role_firewalld_sources:
  - source:
    zone:
    target:
    services:
      - "ssh"
    ports: []
################################################################################

```

Dependencies
------------

none

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

```
---
- name: Example role use
  hosts: all
  roles:
    - role: role-firewalld
      vars:
        role_firewalld_present: true
        role_firewalld_default_zone: "public"
        role_firewalld_interfaces:
          - ifname:
            zone:
            services:
              - "ssh"
              - "https"
	    ports: []
          - ifname: eth1
            zone: work
            services:
              - "syslog"
              - "http"
              - "https"
              - "nfs"
            ports:
              - "8888/tcp"
              - "9999/udp"
```

License
-------

BSD

Author Information
------------------

pja@IT
