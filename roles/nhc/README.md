role-nhc
=========

Role to install Node Health Checker https://github.com/mej/nhc on nodes

Role Variables
--------------

- `nhc_short_hostname` (True): If nodes are called by their shortname  
- `nhc_hw_swap_free` (0): The amount of swap space to check  
- `nhc_hw_mem_free` (1MB): The amount of free memory   
- `nhc_hw_eth` (eth0): The interface to check for active connection  
- `nhc_hw_mcelog`: Check the mcelog daemon for any pending errors.   
- `nhc_mcelog_max_corrected_rate` (100): allow 100 corrected errors/24h.  
- `nhc_fs_mount_check` (list): List of mount points to check
- `gpu` (false): if GPU is available  
- `nhc_checks` (check_reboot_slurm): Additional checks to run  


Example Playbook
----------------

Including an example of how to use your role (for instance, with variables
passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: role-nhc }

License
-------

BSD

Author Information
------------------

Uemit Seren <uemit.seren@gmi.oeaw.ac.at>
