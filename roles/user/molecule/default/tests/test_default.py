from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import crypt
from hmac import compare_digest as compare_hash

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_group_key_created(host):
    g = host.group('user_key')
    assert g.exists
    assert g.gid == 100000


def test_user_key_created(host):
    u = host.user('user_key')
    assert u.name == 'user_key'
    assert u.uid == 100000
    assert u.gid == 100000
    assert u.home == '/home/user_key'
    assert u.shell == '/bin/bash'
    assert u.gecos == 'Managed by tower'


def test_group_linux_created(host):
    g = host.group('user_linux')
    assert g.exists
    assert g.gid == 100001


def test_user_linux_created(host):
    u = host.user('user_linux')
    assert u.name == 'user_linux'
    assert u.uid == 100001
    assert u.gid == 100001
    assert u.home == '/home/user_linux'
    assert u.shell == '/bin/bash'
    assert u.gecos == 'Managed by tower'
    # Passwords
    plain = str('0123456789')
    unix = str(u.password)
    assert compare_hash(crypt.crypt(
        plain, unix),
        unix)


def test_ssh_key_for_key_1_user_deployed(host):
    f = host.file('/home/user_key/.ssh/authorized_keys')
    assert f.exists
    assert f.contains("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQDN4GA0Uz7ati7zIa")


def test_ssh_key_for_key_2_user_deployed(host):
    f = host.file('/home/user_key/.ssh/authorized_keys')
    assert f.exists
    assert f.contains("ssh-rsa DDAAB3NzaC1yc2EAAAADAQABAAAAgQDN4GA0Uz7ati7zIa")


def test_ssh_is_disabled_for_root(host):
    f = host.file('/etc/ssh/sshd_config')
    assert f.exists
    assert f.contains("\nPermitRootLogin no\n")


def test_ssh_is_disabled_for_linux_user(host):
    f = host.file('/etc/ssh/sshd_config')
    assert f.exists
    assert f.contains("\nDenyUsers user_linux\n")


def test_linux_user_has_sudo(host):
    f = host.file('/etc/sudoers.d/system_deployment_user_linux')
    assert f.exists
    assert f.contains("user_linux ALL=(ALL) NOPASSWD: ALL")


def test_key_user_has_sudo(host):
    f = host.file('/etc/sudoers.d/system_deployment_user_key')
    assert f.exists
    assert f.contains("user_key ALL=(ALL) NOPASSWD: ALL")


def test_sshd_is_running(host):
    s = host.service('sshd')
    assert s.is_running


def test_sshd_is_enabled(host):
    s = host.service('sshd')
    assert s.is_enabled
