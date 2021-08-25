Role Name
=========

Role:
* installs [goss](https://github.com/aelsabbahy/goss)
* places a cron file in [/etc/cron.d/prometheus_goss](templates/prometheus_goss.cron.j2)
* places a shell script that is called from cron, runs goss, parses its output and creates a prometheus formated metrics file [prometheus_goss.sh](templates/prometheus_goss.sh.j2)
* places a yaml [goss test file](files/dummy.yml)

Requirements
------------

In order for this to work, prometheus node exporter would be a very cool thing to have installed and configured to use the textfile collector from a certain folder. Rest is pretty simple.

**Limitations**:

* Currently, this role only works with ONE yaml test file. Do not do split test files and includes. TBFixed at some later point in time.

Role Variables
--------------

_defaults/main.yml_

```
goss_version: "0.3.11"
goss_install_dir: "/usr/local/bin"
goss_test_file: "dummy.yml"
# if this is empty, no variable file will be created
goss_template_vars: ""
goss_template_vars_file: "goss_vars.yml"
goss_node_exporter_textfile_dir: "/tmp"

```

* `goss_version` : this one is simple
* `goss_install_dir` : this is where the goss binary, .sh script (called from cron) and the test yaml file will all end
* `goss_test_file` : this is the test filename to deploy (NOTE: place it in **files/** folder next to your playbook)
* `goss_template_vars` : data structure that is dumped to `goss_template_vars_file` and used to template the test, [see here...](https://github.com/aelsabbahy/goss/blob/master/docs/manual.md#templates)
* `goss_node_exporter_textfile_dir` : where prometheus node exporter expects to find the metrics files (ending in .prom)

Dependencies
------------

none.

Example Playbook
----------------

An example playbook might look something like this:

```
---
- hosts: all
  become: false
  gather_facts: true
  vars:
    - goss_version: "0.3.11"
    - goss_install_dir: "/usr/local/bin"
    - goss_test_file: "compute.yml"
    - goss_template_vars:
        pipi: "tutu"
        xxx: 123
        yyy:
          - 1
          - 2
          - 3
    - goss_template_vars_file: "jonny.yml"
    - goss_node_exporter_textfile_dir: "/opt/prometheus_data"


  roles:
    - role-goss

  tasks:
  - name: hello world
    debug:
      msg: "Hello World!"

#
# vim: sts=2:ai:list:cursorcolumn
```

with a _compute.yml_ file under _files/_:

```
root@bimbo:~/src/ansible-goss#cat files/compute.yml
port:
  tcp:6818:
    listening: true
    ip:
    - 0.0.0.0
service:
  slurmd:
    enabled: true
    running: true
process:
  slurmd:
    running: true
```

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
