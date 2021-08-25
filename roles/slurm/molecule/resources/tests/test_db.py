from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('cluster_db')


@pytest.mark.parametrize('pkg', [
    "slurm-slurmdbd"
])
def test_pkgs(host, pkg):
    package = host.package(pkg)
    assert package.is_installed


def test_db_service_running(host):
    db_service = host.service("mariadb")
    assert db_service.is_enabled
    assert db_service.is_running


def test_slurmdbd_service_running(host):
    slurmdbd_service = host.service("slurmdbd")
    assert slurmdbd_service.is_enabled
    assert slurmdbd_service.is_running


def test_munge_service_running(host):
    munge_service = host.service("munge")
    assert munge_service.is_enabled
    assert munge_service.is_running
