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
    f_cs = file.content_string
    loc = '/srv/containers/webservice'
    assert "--name webservice" in f_cs
    assert "--ip 10.88.0.10" in f_cs
    assert "--publish 80:8080" in f_cs
    assert "--publish 443:4433/tcp" in f_cs
    assert "--cap-add=SYS_ADMIN" in f_cs
    assert "--cap-drop=NET_ADMIN" in f_cs
    assert "--device=/dev/random:/srv/random:r" in f_cs
    assert "env-file " + loc + "/environment-file.txt" in f_cs
    assert "--volume " + loc + "/volume_data:/opt/test_1:Z" in f_cs
    assert "--volume " + loc + "/volume_config:/opt/test_2:Z" in f_cs
    assert "--volume /tmp:/mnt" in f_cs
    assert "httpd:2.4.39-alpine" in f_cs


def test_contianer_config_was_modified(host):
    file = host.file('/usr/share/containers/containers.conf')

    assert file.exists
    assert "log_size_max = 104857600" in file.content_string


def test_container_directory_exists(host):
    file = host.file('/srv/containers/webservice')

    assert file.exists
    assert file.is_directory
    assert file.uid == 0
    assert file.gid == 0
    assert file.mode == 0o775


def test_env_file_was_written(host):
    file = host.file('/srv/containers/webservice/environment-file.txt')

    assert file.exists
    assert file.uid == 0
    assert file.gid == 0
    assert file.mode == 0o700
    assert "key_a=value_a" in file.content_string
    assert "key_b=value_b" in file.content_string


def test_volume_directories_were_created(host):
    file = host.file('/srv/containers/webservice/volume_data')

    assert file.is_directory
    assert file.uid == 222
    assert file.gid == 333
    assert file.mode == 0o770

    file = host.file('/srv/containers/webservice/volume_config')

    assert file.is_directory
    assert file.uid == 222
    assert file.gid == 333
    assert file.mode == 0o770


def test_service_is_running(host):
    service = host.service('podman_webservice.service')

    assert service.is_running
    assert service.is_enabled
