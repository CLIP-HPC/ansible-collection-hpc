role-container
==============
* setup the environment for podman containers
    *  Volumes
    *  IP for container network
    *  Environment variables
    *  Certificates
* fetches/updates images and runs them in a persistent way via systemd.

Testing procedure
-----------------
1. Roll TDE content view forward
2. Rebuild the ubi8-tde image & Tag it
3. Update tags in molecule tests


Variables
---------
The role requires a hash role_container_service as input with the whole service specification:
```
role_container_hostname: <string> defaults to inventory_hostname
role_container_certname: <string> override non-default cert common name (which is used as filename, default is the role_container_hostname), see role-digicert: variable role_certificate_hostname
role_container_service:
    name: <string> [required] [a-zA-Z0-9][a-zA-Z0-9_.-]
    image: <string> [required] use the full url of the image
    tag: <string> [required]
    uid: <int> [required]
    gid: <int> [required]
    map_user: <bool> 
    # /etc/hosts entries: "hostname:ip"
    hosts: <list>
      - "other.host.name:1.2.3.4"
    selinux: <boolean> [required]
    # Volumes
    volumes: <list>
      - name: <string>
        path: <string>
        mode: <string>
    # Shares
    shares:
      - src: <string>
        name: <string>
        container: <string>
    hostdirs:
      - src: <string>
        container: <string>
    # Environment Variables
    environment_variables: <hash>
      <string>:<string>
      <string>:<string>
    # Certificates
    certificate: <bool>
    # Network
    ip: <ip_addr>
    # Ports
    ports: <list of hashes>
      - host: <int>
        container: <int>
        protocol: <string> [tcp/udp] [optional in this hash]
```

Host Preperation
----------------
To namespace different containers running on the same host, the <name> variable is used to create the containers home-directory: 
/srv/containers/<name>

Volumes
-------
```
uid: 333
gid: 444
selinux: true
volumes: <list>
    - name: <string>
      path: <string>
    - name: data
      path: /opt/data
      mode: '0700'
    - name: config
      parh: /etc/httpd/config.d
```
Per volume a directory is created: /srv/containers/<name>/volume_<volumes_name>/
The directory will be owned by <uid>:<gid> with a mode of 770
Mounted into the container to <volumes_path>
If selinux is true the :Z flag is added to the podman --volume flag
The mode can overwirte the standard 770 mode for the volume

If your /srv/containers directory is on a NFS share you have to set the selinux to false, otherwise to true

Shares
------
```
shares:
  - src: <string>
    name: <string>
    container: <string>
  - src: 'storage.imp.ac.at:/ifs/groups/vbcf-ngs/'
    name: 'groups_ngs'
    container: '/groups/vbcf-ngs'

```
This option will install nfs-utils, create the folder /srv/shares/ and mount all 'src' folders to the given 'name' within the /srv/shares/<name> folder. The SE-Linux flag will be always ignored. The folder will be mounted as volume into the container with the <contaner> path.
Be aware that the container user needs the permissions to write on this share-volume. (see also map_user flag)

Hostdirs
------
```
hostdirs:
  - src: <string>
    container: <string>
  - src: '/var/lib/sss/pipes/'
    container: '/var/lib/sss/pipes/'
```
Map directories from the host directly to the container. Can be used to expose socket files etc, to the container (i.e. piggybacking on host sssd service or similar).

Command
------
```
cmd: '--default-storage-engine=MyISAM'
```
This can be used to pass a custom CMD to the docker run. 
For example the official MySQL docker container supports this for changing defaults

Mapping User
------------
```
uid: <int> [required]
gid: <int> [required]
map_user: <bool> 

```
The optional map_user flag allows you to run the container in the given <uid>:<gid> context, the image has to be prepared accordingly.
This can be used to mount nfs-share with a service user.
It will result in a docker run command like:
```
--userns host --user <uid>:<gid> 

```

Environment Variables
---------------------
```
environment_variables: <hash>
    <key>:<value>
    PG_PASSWORD: supersecret
```
All key-value pairs in the <environment_variables> hashes are persisted on the host and are injected into the container.

Certificates
------------
```
selinux: false
certificate: <bool>
certificate: true
hostname: <string> defaults to inventory_hostname
hostname: test-1.vbc.ac.at
```
If the <certificate> flag is set to TRUE, the certificate <role_container_hostname>.crt and key <role_container_hostname>.key are available in the /srv/certificates diretory in the container.
The role-certificate has to run before this role, expected host-certificate-directory is /srv/certificates/
If selinux is true the :Z flag is added to the podman --volume flag

Networking
----------
```
ip: <ip_addr>
ip: 10.88.0.10
```
All containers on a host are withing the 10.88.0.0/16 network.
Dueto a missing DNS service (currently under development) in podman, you can set static IPs for each container via the <ip> variable. This is only needed if you have multiple containers that have to talk to each other. Just enumerate them from 10.88.0.10 upwards.

Ulimit
----------
```
ulimits:
  nproc: 65535
  nofile:
    soft: 10000
    hard: 15000
  
```
Override the default ulimits for a container. You can either specify a single limit as an integer or soft/hard limits as a mapping.

Devices
-------
```
privileged: true <bool> optional, default: false

devices:
  - src: /dev/fuse <string>
    container: /dev/fuse <string>
    permissions: rw <string>
```
Maps devices into the container, you will most porbably need some container capabilities to do this.
Permissions is a combination of r for read, w for write, and m for mknod(2).

Capabilities
------------
```
privileged: true # optional, defaults to false

capabilities:
  - name: SYS_ADMIN <string>
    action: add <string> add or drop
```
Sets or drop the container capabilities. See container capabilities: 
https://man7.org/linux/man-pages/man7/capabilities.7.html
The privileged flag gives extended container capabilities, see man docker run.

Systemd
-------
A systemd unit file is created at /etc/systemd/system/podman_<name>.service
The service is always enabled and started.

Requirements
------------

Podman has to be installed on the system, if you want to use the certificate option, run the role-certificate first.


Example Playbook
----------------

- hosts: servers
  roles:
     - { role: role-container, role_container_service: { name: 'webservice', image: "docker.artifactory.imp.ac.at/it/molecule/tests/httpd"
      tag: "2.4.39-alpine", uid: 222, gid: 333 } }


Author Information
------------------

Klaus Rembart <klaus.rembart@imba.oeaw.ac.at>
