from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_service_is_running(host):
    ulimits_dict_service = host.service(
        'podman_ulimits_dict.service'
    )
    ulimits_string_service = host.service(
        'podman_ulimits_string.service'
    )

    assert ulimits_dict_service.is_running
    assert ulimits_dict_service.is_enabled

    # only supported in libpod 1.5.0
    # assert ulimits_string_service.is_running
    assert ulimits_string_service.is_enabled


def test_systemd_unit_file_has_ulimits(host):
    f_name = '/etc/systemd/system/podman_ulimits_dict.service'
    file = host.file(f_name)
    assert "--ulimit nofile=10000:15000" in file.content_string
    assert "--ulimit nproc=65535" in file.content_string

    f_name = '/etc/systemd/system/podman_ulimits_string.service'
    file = host.file(f_name)
    assert "--ulimit host" in file.content_string


def test_ulimits(host):
    nofile = host.check_output(
        'podman exec ulimits_dict bash -c "ulimit -Sn && ulimit -Hn"'
    )
    assert "10000\n15000" == nofile
    noproc = host.check_output(
        'podman exec ulimits_dict bash -c "ulimit -u"'
    )
    assert "65535" == noproc
    # only supported in libpod 1.5.0
    # host = host.check_output(
    #     'podman exec ulimits_string ulimit -Sn && ulimit -Hn'
    # )
