from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import json
import pytest

from testinfra.utils.ansible_runner import AnsibleRunner


DEFAULT_HOST = 'all'

inventory = os.environ['MOLECULE_INVENTORY_FILE']
runner = AnsibleRunner(inventory)
runner.get_hosts(DEFAULT_HOST)


@pytest.mark.parametrize('pkg', [
    "Lmod",
    "git",
    "rdma-core-devel",
    "patch",
    "gcc",
    "gcc-c++",
    "openssl-devel"
])
def test_pkg_installed(host, pkg):
    package = host.package(pkg)
    assert package.is_installed


def test_module_executable(host):
    host.run_test('bash -lc "module --version"')


def test_default_modules(host):
    host.run_expect([0], 'bash -lc "module is-loaded system1"')


def test_lmod_config(host):
    config_cmd = host.run('bash -lc "module --config_json"')
    config_raw = config_cmd.stderr.replace('\\', '').replace('\n', '')
    config = json.loads(config_raw)
    assert len(config['rcfileA']) == 2
    active = config['configT']
    assert active['autoSwap'] == "no"
    assert active['syshost'] == "system1"
    assert active['exactMatch'] == "yes"

    assert active['siteName'] == "VBC"
    assert active['colorize'] == "yes"
    assert active['redirect'] == "no"
    assert active['dot_files'] == "no"
    assert active['pin_v'] == "yes"
    assert active['spdr_loads'] == "yes"


def test_eb_config(host):
    with host.sudo("easybuild"):
        config_cmd = host.check_output('bash -lc "eb --show-config"')
        config_raw = [item for item in config_cmd.split('\n')
                      if not item.startswith('#')]
        config_dict = {}
        for config_line in config_raw:
            config_key, config_value = config_line.split('(E) = ')
            config_dict[config_key.strip()] = config_value.strip()
        base_folder = "/software"
        install_dir = f"{base_folder}/2019"
        assert config_dict['buildpath'] == f"{base_folder}/build-tmp"
        assert config_dict['group-writable-installdir'] == 'True'
        assert config_dict['installpath'] == install_dir
        assert config_dict['prefix'] == install_dir
        assert config_dict['repositorypath'] == f"{install_dir}/ebfiles_repo"


def test_singularity_not_installed(host):
    host.run_expect([1], 'bash -lc "module spider singularity"')
    host.run_expect([1], 'csh -c "module spider singularity"')


def test_sub_shell(host):
    sf = 'z00_lmod.csh'
    if host.system_info.release.split('.')[0] == '8':
        sf = 'modules.csh'
    bash = 'bash -lc \'source ~/.bash_profile && echo "$MODULEPATH"\''
    csh = f'csh -c \'source /etc/profile.d/{sf} && echo "$MODULEPATH"\''
    module_bash_cmd = host.check_output(bash)
    module_csh_cmd = host.check_output(csh)
    assert len(module_bash_cmd.split(':')) == 1
    assert len(module_csh_cmd.split(':')) == 1


def test_eb_search(host):
    with host.sudo("easybuild"):
        search_cmd = host.check_output('bash -lc "eb -S singularity"')
        assert search_cmd != ''
