role-sssd
=========

Configure SSSD on a Linux host to authenticate users from AD

Role Variables
--------------

To join a specific machine into a domain the user MUST provide the variable:

* role_sssd_ad_password: password of the service account used to join the machine into the domain.

and OPTIONALLY:

* role_sssd_domain: VBC or TESTING  domain (defined in vars, default: VBC)
* role_sssd_allowed_groups: list of AD groups allowed to access the machine (default: is.grp)

The vars/main.yml contains the active directory settings for VBC and TESTING (only used for Molecule testing)
The `role_sssd_allowed_groups` variable specifies the AD groups that are allowed to access the machine. By default the is.grp is added.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables
passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: role-sssd, role_sssd_domain: VBC, role_sssd_ad_password: [PASSWORD_OF_JOIN_USER] }

If you want to unenroll a machein from AD you can set `role_sssd_present` to false.

    - hosts: servers
      roles:
         - { role: role-sssd, role_sssd_domain: VBC, role_sssd_present: false, role_sssd_ad_password: [PASSWORD_OF_JOIN_USER] }

License
-------

BSD

Author Information
------------------

* Uemit Seren <uemit.seren@gmi.oeaw.ac.at>
