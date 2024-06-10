from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import pytest
import json

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('cluster_control')


@pytest.mark.parametrize('pkg', [
    "slurm-slurmrestd",
])
def test_pkgs(host, pkg):
    package = host.package(pkg)
    assert package.is_installed


def test_munge_service_running(host):
    munge_service = host.service("munge")
    assert munge_service.is_enabled
    assert munge_service.is_running


def test_slurmrestd_service_running(host):
    slurmrest_service = host.service("slurmrestd")
    assert slurmrest_service.is_enabled
    assert slurmrest_service.is_running


def test_slurmrestd(host):
    rest_url = "http://localhost:6820"
    token = host.check_output("scontrol token lifespan=99999").split("=")[1]
    header = f'-H "X-SLURM-USER-NAME:root" -H "X-SLURM-USER-TOKEN:{token}"'
    ping_cmd = f'curl -s -X GET {header} {rest_url}/slurm/v0.0.41/ping'
    jobs_cmd = f'curl -s -X GET {header} {rest_url}/slurmdb/v0.0.41/jobs'
    ping = json.loads(host.check_output(f"bash -lc '{ping_cmd}'"))
    assert len(ping['errors']) == 0
    assert ping['pings'][0]['pinged'] == 'UP'
    jobs = json.loads(host.check_output(f"bash -lc '{jobs_cmd}'"))
    assert len(jobs['errors']) == 0
    assert len(jobs['jobs']) > 0
