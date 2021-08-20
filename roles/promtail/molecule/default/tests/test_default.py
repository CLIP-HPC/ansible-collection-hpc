from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_config_file(host):
    f = host.file('/etc/promtail/promtail.yml')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'promtail'


def test_promtail_binary(host):
    b = host.file('/opt/promtail/promtail-linux-amd64')

    assert b.exists
    assert b.user == 'root'
    assert b.group == 'promtail'
    assert b.mode == 0o755


def test_promtail_service(host):
    s = host.service('promtail')

    assert s.is_enabled
    assert s.is_running


def test_daemon_listenting(host):
    assert host.socket("tcp://9080").is_listening
