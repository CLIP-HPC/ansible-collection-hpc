from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_pkg_installed(host):
    assert host.package('bash-completion').is_installed


def test_user_scripts(host):
    for f in ['slurm', 'jobinfo']:
        assert host.file('/software/system/utils/%s' % f).exists


def test_skel_files(host):
    for f in ['bash_completion', 'ssh', 'vim']:
        assert host.file('/etc/profile.d/%s.sh' % f).exists
        if f != 'bash_completion':
            assert host.file('/etc/profile.d/%s.csh' % f).exists


def test_new_user(host):
    home = '/home/test'
    host.run('adduser test')
    for f in ['.bashrc', '.emacs', '.kshrc', '.tmuxrc',
              '.vimrc', '.wgetrc', '.inputrc']:
        assert host.file('%s/%s' % (home, f)).exists
    user_cmd = host.run('runuser -l test -- -c "whoami"')
    assert user_cmd.rc == 0
    assert host.file('%s/.ssh' % home).is_directory
    assert host.file('%s/.ssh/id_ecdsa' % home).exists
    assert host.file('%s/.ssh/id_ecdsa.pub' % home).exists
    assert host.file('%s/.ssh/authorized_keys' % home).exists
    assert host.file('%s/.ssh/config' % home).exists
    pub_md5 = host.file('%s/.ssh/id_ecdsa.pub' % home).md5sum
    auth_md5 = host.file('%s/.ssh/authorized_keys' % home).md5sum
    assert pub_md5 == auth_md5
