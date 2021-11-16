from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_pkgs(host):
    package = host.package("sudo")
    assert package.is_installed


def test_sudoers_include_dir(host):
    assert host.file("/etc/sudoers.d").exists


def test_sudoers_file(host):
    assert host.file("/etc/sudoers.d/role_sudoers").exists


def test_sudoers(host):
    sudoers_file = '/etc/sudoers.d/role_sudoers'
    cred1 = "%group1 ALL = (ALL) ALL"
    cred2 = "bar ALL = (ALL) NOPASSWD: ALL"
    cred3 = "%group3 ALL = (user1,user2) AL"
    host.run_expect([0], f'cat {sudoers_file} | grep "{cred1}"')
    host.run_expect([0], f'cat {sudoers_file} | grep "{cred2}"')
    host.run_expect([0], f'cat {sudoers_file} | grep "{cred3}"')
