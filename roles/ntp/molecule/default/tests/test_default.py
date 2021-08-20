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


def test_chrony_package(host):
    pkg = host.package("chrony")
    assert pkg.is_installed


def test_chrony_configuration(host):
    conf = host.file("/etc/chrony.conf")
    assert conf.exists
    assert conf.uid == 0
    assert conf.gid == 0
    assert conf.mode == 0o644


def test_chrony_service(host):
    service = host.service("chronyd.service")
    assert service.is_enabled
    assert service.is_running


def test_timezone(host):
    pkg = host.package("tzdata")
    zonefile = host.file("/etc/localtime")
    assert pkg.is_installed
    assert zonefile.exists
    assert zonefile.is_symlink
    assert zonefile.linked_to == "/usr/share/zoneinfo/Europe/Vienna"
