role-sudoers
=========

- installs sudo package
- ensure that /etc/sudoers.d directory is present and included from sudoers.conf 
- create or remove sudoers file in /etc/sudoers.d

Role Variables
--------------

**defaults**
- role_sudoers_privileges (array of dicts describing sudoers stanzas, see below)
- role_sudoers_present (true/false flag, to deploy the sudoers file or remove it)

Flags for *role_sudoers_privileges*:

- name (user/%group name to be allowed privilege change)
- nopasswd (yes/no, unspecified default: NO)
- runas (comma separated list of allowed target users, unspecified default: ALL)


Example Playbook
----------------

Including an example of how to use your role (for instance, with variables
passed in as parameters) is always nice for users too:

    - hosts: servers
      vars:
        role_sudoers:
          - name: '%group1'
          - name: 'bar'
            nopasswd: true
          - name: '%group3'
            runas: user1,user2
      roles:
         - { role: role-sudoers }

To remove the sudoers file just pass `role_sudoers_present=false` to the role.

License
-------

BSD

Author Information
------------------

Uemit Seren <uemit.seren@gmi.oeaw.ac.at>
