from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_enrolled(host):
    host.run_expect([1], 'realm list | grep imp.univie.ac.at')


def test_ad_user(host):
    host.run_expect([1], 'id svc_realmd_test_join@IMP.UNIVIE.AC.AT')
