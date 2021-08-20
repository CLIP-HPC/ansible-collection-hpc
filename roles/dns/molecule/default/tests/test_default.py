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


def test_alias_1(host):
    cmd = host.run("/bin/host test-999-"
                   + os.environ.get("INSTANCE_ID") + ".vbc.ac.at ns.imp.ac.at")
    assert not cmd.rc
    cmd = host.run("/bin/host test-999-"
                   + os.environ.get("INSTANCE_ID")
                   + "-1.vbc.ac.at ns.imp.ac.at")
    assert not cmd.rc
    cmd = host.run("/bin/host test-999-"
                   + os.environ.get("INSTANCE_ID")
                   + "-2.vbc.ac.at ns.imp.ac.at")
    assert not cmd.rc
