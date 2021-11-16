from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('syslog-server')

client_hostname = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('syslog-client')


# test if service is active
def test_rsyslog(host):
    service_name = 'rsyslog'
    rsyslog = host.service(service_name)

    assert rsyslog.is_running
    assert rsyslog.is_enabled


# make sure syslog ports are listening
def test_logging_ports(host):
    assert host.socket("udp://514").is_listening
    assert host.socket("tcp://514").is_listening


# test if per-host logs work
def test_host_logs(host):
    # file checks run as shell commands, should work with globs
    # domain = "syslog-net-{0}".format(os.environ.get("INSTANCE_ID"))
    client_name = "syslog-client"
    client_fqdn = client_name + ".logtest"
    log_file = f"/var/log/host/{client_fqdn}/{client_fqdn}.log"

    assert host.file(log_file).exists
    # hostname in container is syslog-client
    assert host.file(log_file).contains(client_name)


# test if per priority logs work
def test_prio_logs(host):
    assert host.file("/var/log/logrule/crit.log").contains("crit")
    assert host.file("/var/log/logrule/emerg.log").contains("emerg")
