from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('cluster_login')


@pytest.mark.parametrize('pkg', [
    "slurm",
    "munge",
    "slurm-slurmd"
])
def test_pkgs(host, pkg):
    package = host.package(pkg)
    assert package.is_installed


def test_no_slurm_configs(host):
    assert not host.file('/etc/slurm/').exists


def test_bash_completion_files(host):
    assert host.file('/etc/bash_completion.d/slurm_completion.sh').exists


def test_munge_service_running(host):
    munge_service = host.service("munge")
    assert munge_service.is_enabled
    assert munge_service.is_running


def test_slurmd_service_running(host):
    slurmd_service = host.service("slurmd")
    assert slurmd_service.is_enabled
    assert slurmd_service.is_running


def test_sinfo(host):
    output = ("PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST\n"
              "compute1*    up   infinite      1   idle cluster-compute1-0\n"
              "compute2     up   infinite      2   idle cluster-compute1-0,cluster-compute2-0")  # noqa E501
    sinfo_output = host.check_output("bash -lc 'sinfo'")
    assert sinfo_output == output


def test_sacctmgr(host):
    output = "cluster|6817|short"
    cmd = "bash -lc 'sacctmgr list -nP cluster format=cluster,ControlPort,QOS'"
    sacct_output = host.check_output(cmd)
    assert sacct_output == output


def test_srun(host):
    srun_output = host.check_output("bash -lc 'srun --qos=short hostname'")
    assert srun_output.strip() == "cluster-compute1-0"


def test_sbatch(host):
    sbatch_cmd = "sbatch --parsable --comment=test --wrap hostname"
    cmd = f"bash -lc 'TEST_ENV=test {sbatch_cmd}'"
    job_id = host.check_output(cmd)
    # check submitline
    submit_line_cmd = f"bash -lc 'sacct -P -j {job_id} -o submitline%50'"

    # required because it takes a bit until it shows up
    for i in range(100):
        job_state = host.check_output(submit_line_cmd)
        if sbatch_cmd in job_state:
            break
    submit_line = host.check_output(submit_line_cmd)
    assert sbatch_cmd in submit_line

    # check comment
    comment_cmd = f"bash -lc 'sacct -P -j {job_id} -o comment'"
    comment = host.check_output(comment_cmd)
    assert 'test' in comment

    # check job envs
    job_env_cmd = f"bash -lc 'sacct -j {job_id} --env-vars | grep TEST_ENV'"
    assert host.run_expect([0], job_env_cmd)

    # check batch script
    script = f"""Batch Script for {job_id}
--------------------------------------------------------------------------------
#!/bin/sh
# This script was created by sbatch --wrap.

hostname

    """
    batch_cmd = f"bash -lc 'sacct -j {job_id} --batch'"
    batch_script = host.check_output(batch_cmd)
    assert batch_script.strip() == script.strip()


def test_sacct(host):
    sacct_output = host.check_output("bash -lc 'sacct'")
    assert len(sacct_output.split('\n')) >= 3


def test_qos(host):
    output = ("normal|0||||\n"
              "short|4|cpu=12,mem=10G|cpu=5,mem=5G|cpu=5,mem=5G|08:00:00")
    cmd = "bash -lc 'sacctmgr -nP show qos format=Name,Priority,GrpTRES,MaxTRES,MaxTRESPerUser,MaxWALL'"  # noqa: E501
    qos_output = host.check_output(cmd)
    assert qos_output == output


def test_part_quos(host):
    cmd = "bash -lc 'scontrol show part compute1 -o | grep AllowQos=short'"
    assert host.run_expect([0], cmd)
    cmd = "bash -lc 'scontrol show part compute2 -o | grep AllowQos=short'"
    assert host.run_expect([0], cmd)


def test_srun_with_features(host):
    cmd = "bash -lc 'srun --qos=short -C special hostname'"
    srun_output = host.check_output(cmd)
    assert srun_output.strip() == "cluster-compute1-0"
