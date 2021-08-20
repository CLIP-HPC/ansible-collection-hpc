Role Name
=========

role-ntp
- installs [chrony](https://chrony.tuxfamily.org) and configures it in client mode
- sets timezone

Requirements
------------

System has access to yum repositories with the following packages:
- tzdata
- chrony

Role Variables
--------------

defaults/main.yml

```
role_ntp_servers:
  - "time.imp.ac.at"
#  - list of ntp servers to be configured

role_ntp_timezone: "Europe/Vienna"
```


Dependencies
------------

None

Example Playbook
----------------


Minimal playbook, default variables:

```
---
- hosts: localhost

  roles:
    - role-ntp
```


Playbook that overrides default role_ntp_timezone:

```
---
- hosts: localhost

  roles:
    - role: role-ntp
      role_ntp_timezone: "Europe/Zagreb"
```


License
-------

BSD

Author Information
------------------

pja@IT
