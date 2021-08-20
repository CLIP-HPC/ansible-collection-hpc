from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_hosts_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


def test_firewalld_service(host):
    s = host.service('firewalld')

    assert s.is_enabled
    assert s.is_running


def test_zone(host):
    t = host.run('/usr/bin/firewall-cmd --get-active-zones |grep public')

    assert not t.rc


def test_services(host):
    t = host.run('/usr/bin/firewall-cmd '
                 + '--list-services --zone public|grep -E "^ssh$"')

    assert not t.rc


def test_ports(host):
    t = host.run('/usr/bin/firewall-cmd '
                 + '--list-ports --zone public|grep -E "^9999/udp$"')

    assert not t.rc
