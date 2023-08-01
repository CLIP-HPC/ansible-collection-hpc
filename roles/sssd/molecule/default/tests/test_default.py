"""Role testing files using testinfra."""
import pytest


@pytest.mark.parametrize('pkg', [
                         'realmd',
                         'sssd',
                         'oddjob',
                         'oddjob-mkhomedir',
                         'adcli',
                         'samba-common-tools'
                         ])
def test_pkgs(host, pkg):
    package = host.package(pkg)
    assert package.is_installed


def test_realmd_conf(host):
    assert host.file("/etc/realmd.conf").exists


def test_ssssd_running(host):
    sssd_service = host.service("sssd")
    assert sssd_service.is_enabled
    assert sssd_service.is_running


def test_enrolled(host):
    host.run_expect([0], 'realm list | grep imp.univie.ac.at')


def test_ad_user(host):
    user = host.user('svc_realmd_test_join@IMP.UNIVIE.AC.AT')
    assert user.name == 'svc_realmd_test_join@IMP.UNIVIE.AC.AT'
    assert user.uid == 560427


def test_permit(host):
    ap = "access_provider = simple"
    host.run_expect([0], f'cat /etc/sssd/sssd.conf | grep "{ap}"')
    host.run_expect([0], 'cat /etc/sssd/sssd.conf | grep is.grp')


def test_password_auth_enabled(host):
    pw = "^PasswordAuthentication yes"
    host.run_expect([0], f'cat /etc/ssh/sshd_config | grep "{pw}"')


def test_override_homedir(host):
    homedir = "override_homedir = /users/%u"
    host.run_expect([0], f'cat /etc/sssd/sssd.conf | grep "{homedir}"')


def test_sss_sshd_public_key(host):
    user = 'svc_realmd_test_join@IMP.UNIVIE.AC.AT'
    key = host.run(f"sudo -u nobody /usr/bin/sss_ssh_authorizedkeys {user}")
    assert key.succeeded
    assert key.stdout == 'dummy-invalid-demo-key\n'
