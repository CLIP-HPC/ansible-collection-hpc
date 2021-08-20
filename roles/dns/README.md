Role Name
=========

Role adds to existing infoblox host record a list of aliases.

**NOTE: any already existing aliases will be wiped and replaced with the here specified list!!!**

Requirements
------------

Role requires ```pip install infoblox-client``` python module to be installed on the host/environment where it is being called from.

On MacOSX
---------
If ansible workers, forks() are crashing on MacOSx
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES


1Password
---------
Add a 1password file as env variable, with your login information:

```
---
onepass_password: your password
onepass_secret_key: your secret key
onepass_domain: vbc01
onepass_email: your email
```

export ONEPASS_VARS=/Users/username/.1password.yaml
molecule test


Role Variables
--------------

Role **requires** three parameters to execute.

```
---
# defaults file for role-dns
#
# example:
#
# role_dns_hostname: cert-test-1.vbc.ac.at
# role_dns_aliases:
#   - san1-cert-test.vbc.ac.at
#   - san2-cert-test.vbc.ac.at
#
role_dns_hostname: ''
role_dns_aliases: []
```

and the third parameter `nios_provider` must be a dict containing:
```
nios_provider:
  host:
  username:
  password:
```

Dependencies
------------

None.

Example Playbook
----------------

Example playbook with all the variables needed and nios_provider coming from vault:

```
---
- hosts: all

  roles:
    - role: role-dns
      nios_provider: "{{ vault_role_dns_nios_provider }}"
      role_dns_hostname: "cert-test-1.vbc.ac.at"
      role_dns_aliases:
        - san1-cert-test.vbc.ac.at
        - san2-cert-test.vbc.ac.at
```

License
-------

BSD

Author Information
------------------

pja@IT
