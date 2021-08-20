Role Name
=========

Manage Certificates via the Sectigo ACME endpoint, using DNS-01 challenge.

Requirements
------------

The role needs the "PyOpenSSL>=0.15" pip package - to minimize the installed packages on the host system, all certificate related actions are performed in a local python environment (or tower environment).
For sectigo:
* requires inforblox-client (pip install) to setup DNS TXT challenge records
* Infoblox: service user must have permissions to create TXT records in the respective zones

Role Variables
--------------

This playbooks expects the following variables:
    
    role_certificate_hostname: # common certificate name, defaults to inventory hostname
    # SAN - Subject alternativ names for certificate
    role_certificate_aliases:
        - san1-cert-test.vbc.ac.at
        - san2-cert-test.vbc.ac.at
    # Final certificate directory on remote host
    role_certificate_tls_dir: /srv/certificates/
    # Days left before renwal is triggered
    role_certificate_renew_days: 31
    # Sectigo ACME
    role_certificate_provider:
      type: acme
      directory: "sectigo directory id i.e. https://acme.sectigo.com/v2/OV"
      account_id: "sectigo account_id"
      account_uri: "https://acme.sectigo.com/v2/OV/account/< sectigo account_id>"
      account_key: " account_key from 1password | replace('\\n', '\n') "
    # Infoblox credentials for TXT ACME DNS-01 challenge records, same as for role-dns
    role_certificate_nios_provider:
      host: ns.imp.ac.at
      username: "svc_infoblox_ansible"
      password: "secret password"

Workflow
--------

1. A local temporary directory is created.
2. From the <role_certificate_tls_dir>, the <role_certificate_hostname>.[crt,csr,key] files are copied to the tmp dir.
3. Check if cert is valid/exists or reissue/create a new certificate
4. Copy files back to:
    <role_certificate_tls_dir>/<role_certificate_hostname>.[crt,csr,key]

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:
```
- hosts: servers
  roles:
    - role: role-certificate
      role_certificate_hostname: cert-test-1.vbc.ac.at # uses inventory_hostname if not specified
      role_certificate_aliases:
          - san1-cert-test.vbc.ac.at
          - san2-cert-test.vbc.ac.at
      role_certificate_tls_dir: /srv/certificates/
      role_certificate_renew_days: 31
      # Sectigo ACME
      role_certificate_provider:
        type: acme
        directory: "sectigo directory id i.e. https://acme.sectigo.com/v2/OV"
        account_id: "sectigo account_id"
        account_uri: "https://acme.sectigo.com/v2/OV/account/< sectigo account_id>"
        account_key: "account_key | replace('\\n', '\n')"
      # Infoblox credentials for TXT ACME DNS-01 challenge records, same as for role-dns
      role_certificate_nios_provider:
        host: ns.imp.ac.at
        username: "svc_infoblox_ansible"
        password: "secret password"
```

Notes on Sectigo ACME
---------------------

Before external account binding of ACME account becomes possible: 
You need to create an account binding using the HMAC key from the Sectigo portal (https://cert-manager.com/customer/ACOnet).

More specifically, this is ACME external account binding see: https://tools.ietf.org/html/rfc8555#section-7.3.4

Currently, EFF certbot (https://certbot.eff.org/docs/) appears to be the only client implementation supporting this initial step (from ACME HMAC to private key)
```
certbot --config-dir certbot/config \
  --work-dir certbot/work \
  --logs-dir  certbot/logs \
  register \
  --email it_svc_account@vbc.ac.at \
  --server https://acme.sectigo.com/v2/OV \
  --eab-kid  <KEY_ID_FROM_SECTIGO_PORTAL> \
  --eab-hmac-key <HMAC_KEY_FROM_SECTIGO_PORTAL> \
  --agree-tos
```

This will write the key in json JWK format to the config-dir in a file `private_key.json`.

*Note:* the email address will show up in the Sectigo certificate manager portal as "external requester". 
Certificate expiration notifications etc. will also be sent to this email address.

The Ansible ACME certificate client requires the account key in PEM format.
To convert to PEM format, use Python `jwcrypto`, see https://jwcrypto.readthedocs.io/en/latest/jwk.html
```
# install package
$ pip install jwcrypto
#start Python3;
$ python3
# python source:
import jwcrypto.jwk as jwk
import json
private_key = json.load(open('<path_to_config_directory>/accounts/acme.sectigo.com/v2/OV/71905e67ace9b0a25b4117cb76da49bb/private_key.json'))
jwk_key = jwk.JWK()
jwk_key.import_key(**private_key)
jwk_key.export_to_pem(private_key=True, password=None)

# [dumps PEM string of private key, without password]
b'-----BEGIN PRIVATE KEY-----\nMIIEvAIB.......==\n-----END PRIVATE KEY-----\n'
```

Store the PEM encoded private key with raw line breaks (\n) in 1Password (item: Sectigo), 
the role will properly unescape the linebreaks when reading the private key.

## Molecule setup

1. Download one password cli and add it to your systempath
2. Create a file holding following information, see 1password for the service account (eg ~/.op/molecule)
onepass_password: passwort
onepass_secret_key: seckey
onepass_domain: vbc01
onepass_email: 1password@imba.oeaw.ac.at
3. export ONEPASS_VARS=/home/my.name/.op/molecule
 
## Caveat
For DCV pre-validated domains, sectigo will return a challenge of type "sectigo-dns-01" and state "valid". This breaks with the Ansible module in 2.8.7.
However in upstream code, there is a patch (simply skipping already valid challenges), I've backported this to the copy in the module in library/acme_certificate.py
This works for both DCV pre-validated (where challenge TXT records will be an empty list) and and non-DCV domains.

This workaround is expected to break with Ansible 2.9+ and needs to be re-evaluated for future versions.
