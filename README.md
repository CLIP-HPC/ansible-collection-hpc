# Ansible Collection: clip.hpc

This repo hosts the `clip.hpc` Ansible Collection.

The collection includes the roles to deploy the CBE HPC cluster.

## Installation and Usage

Before using the `clip.hpc` collection, you need to install the collection with the `ansible-galaxy` CLI:

`ansible-galaxy collection install clip.hpc`

You can also include it in a `requirements.yml` file and install it through `ansible-galaxy collection install -r requirements.yml` using the format:

```yaml
collections:
- name: clip.hpc
```

## Roles

Roles in this collection:

- [roles/doca](roles/doca): Installs and configures NVIDIA DOCA drivers for Mellanox NICs.
- [roles/multirail](roles/multirail): Sets up NetworkManager multirail for dual-interface hosts.
- [roles/rocev2](roles/rocev2): Tunes Mellanox NIC firmware for RoCEv2 with DSCP-based QoS.
- [roles/slurm](roles/slurm): Deploys and configures a functional SLURM cluster.
