from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_certificate_was_copied(host):
    loc = '/srv/containers/webservice/certificates/it-webserver-1.vbc.ac.at.'
    for ext in ['crt', 'key']:
        file = host.file(loc + ext)
        assert file.exists
        assert file.uid == 222
        assert file.gid == 333
        assert file.mode == 0o500


def test_systemd_unit_file_was_written(host):
    file = host.file('/etc/systemd/system/podman_webservice.service')

    assert file.exists
    assert file.uid == 0
    assert file.gid == 0
    assert file.mode == 0o644
    assert "--name webservice" in file.content_string
    s = '--volume /srv/containers/webservice/certificates:/srv/certificates:Z'
    assert s in file.content_string
    assert "httpd:2.4.39-alpine" in file.content_string


def test_service_is_running(host):
    service = host.service('podman_webservice.service')

    assert service.is_running
    assert service.is_enabled
