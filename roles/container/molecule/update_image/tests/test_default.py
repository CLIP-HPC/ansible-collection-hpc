from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_systemd_unit_file_was_written(host):
    file = host.file('/etc/systemd/system/podman_webservice.service')

    assert file.exists
    assert file.uid == 0
    assert file.gid == 0
    assert file.mode == 0o644
    assert "--name webservice" in file.content_string
    assert "httpd:2.4.39-alpine" in file.content_string


def test_service_is_running(host):
    service = host.service('podman_webservice.service')

    assert service.is_running
    assert service.is_enabled


def test_image_cleanup(host):
    cmd = host.run(
        "podman image ls --noheading --filter='dangling=true'"
    )
    assert cmd.succeeded
    assert cmd.stdout == ''
