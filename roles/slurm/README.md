# role-slurm

This Ansible role is used to have a fully functional SLURM Cluster

Role Variables
--------------

`role_slurm_service_enabled`: checks whether `role_slurm_service` is enabled

`role_slurm_service`: name of the slurm service e.g. `slurmd`

`role_slurm_control_host`: ansible host name of the controller e.g `"{{ groups['cluster_control'] | first }}"`

`role_slurm_db_host`: ansible host name of the slurmdbd e.g `"{{ groups['cluster_db'] | first }}"`

`role_slurm_partitions`: list of slurm partitions

`role_slurm_cluster_name`: name of the cluster

`role_slurm_enable`:

* `db`: whether to enable db host
* `control`: whether to enable control host
* `batch`: whether to enable compute nodes
* `runtime`: whether to enable SLURM runtime

Example Playbook
----------------

To deploy, create a playbook which looks like this:

    ---
    - hosts:
      - cluster_control
      - cluster_batch
      - cluster_db
      - cluster_login
      become: yes
      roles:
        - role: role-slurm
          role_slurm_enable:
            db: "{{ inventory_hostname in groups['cluster_db'] }}"
            control: "{{ inventory_hostname in groups['cluster_control'] }}"
            batch: "{{ inventory_hostname in groups['cluster_batch'] }}"
            slurmd: "{{ inventory_hostname in not in (grops['cluster_db'] + groups['cluster_control'])}}"
            runtime: true
          role_slurm_db_host: "{{ groups['cluster_db'] | first }}"
          role_slurm_control_host: "{{ groups['cluster_control'] | first }}"
          role_slurm_partitions:
            - name: "compute"
              flavor: "compute-A"
              num_nodes: 8
          role_slurm_cluster_name: cluster
          role_slurm_db_root_password: "test"
    ...

Example Inventory
-----------------

And an Ansible inventory as this:

    [cluster_login]
    cluster-login-0 ansible_host=10.60.253.40 ansible_user=centos

    [cluster_control]
    cluster-control-0 ansible_host=10.60.253.42 ansible_user=centos

    [cluster_db]
    cluster-db-0 ansible_host=10.60.253.41 ansible_user=centos

    [cluster_compute]
    cluster-compute-0 ansible_host=10.60.253.33 ansible_user=centos

    [cluster_db:children]
    cluster_db

    [cluster_control:children]
    cluster_control

    [cluster_batch:children]
    cluster_compute
