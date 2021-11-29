from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_pkgs(host):
    package = host.package("lbnl-nhc")
    assert package.is_installed


def test_files(host):
    host.file("/etc/nhc/nhc.conf").exists
    host.file("/etc/nhc/scripts/goss.nhc").exists
    host.file("/etc/nhc/scripts/nvidia_smi.nhc").exists
    host.file("/etc/nhc/scripts/nvidia_smi_page_retirement.nhc").exists
    host.file("/etc/nhc/scripts/sssd.nhc").exists


def test_nhc_rc(host):
    host.run_expect([0], '/usr/sbin/nhc -d -t 0 MARK_OFFLINE=0 ')
