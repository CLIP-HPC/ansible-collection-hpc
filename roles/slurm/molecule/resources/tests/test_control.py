from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('cluster_control')


@pytest.mark.parametrize('pkg', [
    "slurm-slurmctld",
    "slurm",
    "munge",
    "slurm-example-configs",
])
def test_pkgs(host, pkg):
    package = host.package(pkg)
    assert package.is_installed


def test_munge_service_running(host):
    munge_service = host.service("munge")
    assert munge_service.is_enabled
    assert munge_service.is_running


def test_slurmctld_service_running(host):
    slurmctld_service = host.service("slurmctld")
    assert slurmctld_service.is_enabled
    assert slurmctld_service.is_running


def test_mailx_binary(host):
    assert host.exists("mailx")


def test_job_container_file(host):
    assert host.file('/etc/slurm/job_container.conf').exists
