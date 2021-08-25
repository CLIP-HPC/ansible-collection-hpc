role-lmod
=========

This role sets the environment module and easybuild up for a batch scheduling system

Role Variables
--------------

- `role_lmod_base_folder` (/software): ROOT path for LMOD build environment and other easybuild related files
- `role_lmod_build_env` (2019): The build environment.
- `role_lmod_easyblock_repo` (optional): Link to gitrepo with custom easyblocks
- `role_additional_modules` ([]): List of additional modules to load when the user logs in

There are some additional variables in default/main.yml for LMOD which can be overwritten.
The playbook will create a default system folder inside `role_lmod_base_folder` where a module for the user environment and a module for the build environment (`role_lmod_build_env`) will be placed. Additionally the latest easybuild will be installed inside the build environment and added to the default module load list
of the user environment.
To load additional modules by default add ("MODULE/VERSION") to the `role_additional_modules` variables.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables
passed in as parameters) is always nice for users too:

    - hosts: cluster
      roles:
         - { role: role-lmod, role_additional_modules:['singularity/1.4.2'], role_lmod_base_folder: ['/nfsshare/software'], 'role_lmod_build_env': 2020 }

License
-------

BSD

Author Information
------------------

Uemit Seren <uemit.seren@gmi.oeaw.ac.at>
