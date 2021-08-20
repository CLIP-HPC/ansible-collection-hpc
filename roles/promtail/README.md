Role Name
=========

role-promtail
- installs and configures promtail agent to ship logs to Loki

Requirements
------------

System has access to dnf repos with the unzip package.

Role Variables
--------------

From the role defaults vars:
```
---
# user under which promtail will run
role_promtail_user: promtail
# primary group of the user
role_promtail_group: promtail
# additional groups the user is a member of
# (e.g. to have access to the systemd journal)
role_promtail_additional_groups: systemd-journal
# Base directory for promtail installation
role_promtail_basedir: /opt/promtail
# Path for the promtail binary
role_promtail_bin_path: "{{ role_promtail_basedir }}/promtail-linux-amd64"
# Path for promtail configuration
role_promtail_confdir: /etc/promtail
# Promtail version to install
role_promtail_version: 2.0.0
# Where to get the packed binary
role_promtail_source_uri: "https://github.com/grafana/loki/releases/download/v{{ role_promtail_version }}/promtail-linux-amd64.zip"
# Promtail configuration
role_promtail_config_server:
  http_listen_port: 9080
  grpc_listen_port: 0
role_promtail_config_positions:
  filename: "{{ role_promtail_basedir }}/positions.yml"
role_promtail_loki_server_url: http://127.0.0.1:3100
role_promtail_config_clients:
  - url: "{{ role_promtail_loki_server_url }}/loki/api/v1/push"
role_promtail_config_scrape_configs:
  - job_name: journal
    journal:
      max_age: 12h
      labels:
        job: systemd-journal
    relabel_configs:
      - source_labels: ['__journal__systemd_unit']
        target_label: 'unit'
  - job_name: syslog
    syslog:
      listen_address: 127.0.0.1:6514
      labels:
        job: syslog
    relabel_configs:
    - source_labels:
      - __syslog_message_hostname
      target_label: host
    - source_labels:
      - __syslog_message_app_name
      target_label: application
    - source_labels:
      - __syslog_message_severity
      target_label: severity

```

Dependencies
------------

None

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: myhost
      roles:
        - role-promtail
          role_promtail_loki_server_url: http://myloki.local:3100

License
-------

BSD

Author Information
------------------

martin.gollowitzer@imp.ac.at
