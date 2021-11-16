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
        assert host.file(f"/software/system/utils/{f}").exists


def test_skel_files(host):
    for f in ['bash_completion', 'ssh', 'vim']:
        assert host.file(f"/etc/profile.d/{f}.sh").exists
        if f != 'bash_completion':
            assert host.file(f"/etc/profile.d/{f}.csh").exists


def test_new_user(host):
    home = '/home/test'
    host.run('adduser test')
    for f in ['.bashrc', '.emacs', '.kshrc', '.tmuxrc',
              '.vimrc', '.wgetrc', '.inputrc']:
        assert host.file(f"{home}/{f}").exists
    user_cmd = host.run('runuser -l test -- -c "whoami"')
    assert user_cmd.rc == 0
    assert host.file(f"{home}/.ssh").is_directory
    assert host.file(f"{home}/.ssh/id_ecdsa").exists
    assert host.file(f"{home}/.ssh/id_ecdsa.pub").exists
    assert host.file(f"{home}/.ssh/authorized_keys").exists
    assert host.file(f"{home}/.ssh/config").exists
    pub_md5 = host.file(f"{home}/.ssh/id_ecdsa.pub").md5sum
    auth_md5 = host.file(f"{home}/.ssh/authorized_keys").md5sum
    assert pub_md5 == auth_md5
