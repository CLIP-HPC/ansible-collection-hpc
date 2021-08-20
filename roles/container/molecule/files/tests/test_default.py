from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_file_1_is_created(host):
    file = host.file('/srv/containers/webservice/files')

    assert file.is_directory
    assert file.uid == 222
    assert file.gid == 333
    assert file.mode == 0o770


def test_systemd_unit_file_was_written(host):
    file = host.file('/etc/systemd/system/podman_webservice.service')
    location = '/srv/containers/webservice/files/'
    assert file.exists
    assert file.uid == 0
    assert file.gid == 0
    assert file.mode == 0o644
    assert "--name webservice" in file.content_string
    assert location + "test-1.txt:/opt/test-a.txt:Z" in file.content_string
    assert location + "test-2.txt:/opt/test-b.txt:Z" in file.content_string
    assert "httpd:2.4.39-alpine" in file.content_string


def test_service_is_running(host):
    service = host.service('podman_webservice.service')

    assert service.is_running
    assert service.is_enabled
