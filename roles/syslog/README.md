Role role-syslog
=========

Server mode: deploy syslog server for per host logging
Client mode: deploy client, with setup to forward UDP syslog to the server

Requirements
------------

On RHEL7/8 it will require a correct firewalld setup on the server side.

Role Variables
--------------
From the role defaults vars:
```
---
# mode is eitehr "client" or "server" and will deploy the appropriate side of syslog
role_syslog_mode: "client" 
# the target host for syslog clients
role_syslog_server: syslog.vbc.ac.at
```

Dependencies
------------

None.

Example Playbook
----------------

For client (assuming role\_syslog\_server was set globally to the correct name, client mode is default):
```
---
- hosts: syslog-clients
  roles:
    - role: role-syslog
```


For server
```
---
- hosts: syslog-server
  roles:
    - role: role:syslog
      role_syslog_mode: "server"
```

License
-------

BSD

Author Information
------------------

Erich Birngruber <erich.birngruber@gmi.oeaw.ac.at> (@ebirn)
