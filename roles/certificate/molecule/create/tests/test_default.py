from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import testinfra.utils.ansible_runner

# testinfra_hosts = ["localhost"]
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_remote_tls_dir_created(host):
    f = host.file('/srv/certificates')
    assert f.exists
    assert f.is_directory
    assert f.uid == 0
    assert f.gid == 0
    assert f.mode == 0o700


def test_copy_remote_to_local(host):
    for ext in ['csr', 'crt', 'key']:
        f = host.file('/srv/certificates/cert-sectigo-test-1.vbc.ac.at.' + ext)
        assert f.exists
        assert f.uid == 0
        assert f.gid == 0
        assert f.mode == 0o600
