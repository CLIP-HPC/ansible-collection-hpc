from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('cluster_batch')


@pytest.mark.parametrize('pkg', [
    "libicu",
    "numactl",
    "slurm",
    "munge",
    "slurm-pam_slurm",
    "slurm-libpmi",
    "slurm-slurmd"
])
def test_pkgs(host, pkg):
    package = host.package(pkg)
    assert package.is_installed


def test_no_slurm_configs(host):
    assert not host.file('/etc/slurm/').exists


def test_munge_service_running(host):
    munge_service = host.service("munge")
    assert munge_service.is_enabled
    assert munge_service.is_running


def test_slurmd_service_running(host):
    slurmd_service = host.service("slurmd")
    assert slurmd_service.is_enabled
    assert slurmd_service.is_running


def test_systemd_login_not_running(host):
    systemd_login_service = host.service("systemd-logind")
    assert not systemd_login_service.is_enabled
    assert not systemd_login_service.is_running


def test_pam_d_adopt(host):
    sshd_file = '/etc/pam.d/sshd'
    adopt = "pam_slurm_adopt.so"
    host.run_expect([0], 'cat %s | grep "%s"' % (sshd_file, adopt))


def test_pam_d_not_systemd(host):
    system_auth_file = '/etc/pam.d/system-auth'
    password_auth_file = '/etc/pam.d/password-auth'
    systemd = "pam_systemd"
    host.run_expect([1], 'cat %s | grep "%s"' % (system_auth_file, systemd))
    host.run_expect([1], 'cat %s | grep "%s"' % (password_auth_file, systemd))


def test_pam_ssh_access(host):
    access_file = '/etc/security/access.conf'
    admin_group = "admins"
    command = 'cat %s | egrep "%s"'
    host.run_expect([0], command % (access_file, "^\\+:%s:ALL$" % admin_group))


def test_pam_slurm_exists(host):
    assert host.file('/etc/pam.d/slurm').exists
