role-base-user
=========

This role deploys the two base-users that should be available on each system and disables the root account.

* Ansible tower user: has a public key deployed and ssh enabled (no password set)
* Fallback user: has a password set and ssh disabled 

Role Variables
--------------

**role_base_user_publickey_username**: The user name of the ansible tower automation user (e.g. ansible)
**role_base_user_publickey_key**: A list of public key for the ansible tower automation user (list of strings)
**role_base_user_linux_username**: The user name of the console only fallback user (e.g. fallback)
**role_base_user_linux_password**: The password (plain text) of the fallback user (string)


Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: role-base-user, role_base_user_publickey_username: 'ansible', role_base_user_publickey_key: ['###', '###'], role_base_user_linux_username: 'fallback', role_base_user_linux_password: 'plain_text_password' }


Author Information
------------------

Klaus Rembart <klaus.rembart@imba.oeaw.ac.at>
