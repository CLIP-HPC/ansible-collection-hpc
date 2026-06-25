# Copyright (c) 2019 StackHPC Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
  name: config2dict
  short_description: Convert C(scontrol show config) output to a dict
  version_added: "1.0.0"
  description:
    - Convert a sequence of output lines from C(scontrol show config) to a dict.
    - Uppercase keys are derived parameters per the C(scontrol) man page; mixed case keys come from config files.
    - V((null)) and V(n/a) values are converted to V(null).
    - V(yes)/V(no) values are converted to V(true)/V(false).
    - All other values remain as strings.
  positional: value
  options:
    value:
      description:
        - Lines from C(scontrol show config) output.
      type: list
      elements: str
      required: true
"""

EXAMPLES = r"""
- name: Fetch Slurm configuration
  ansible.builtin.command: scontrol show config
  register: scontrol_output

- name: Convert output to dict
  ansible.builtin.set_fact:
    slurm_config: "{{ scontrol_output.stdout_lines | clip.hpc.config2dict }}"
"""

RETURN = r"""
  _value:
    description: Dictionary of Slurm configuration key-value pairs.
    type: dict
"""

from ansible import errors


def config2dict(lines):
    """Convert a sequence of output lines from `scontrol show config` to a dict.

    As per man page uppercase keys are derived parameters, mixed case are from
    from config files.

    The following case-insensitive conversions of values are carried out:
    - '(null)' and 'n/a' are converted to None.
    - yes and no are converted to True and False respectively

    Except for these, values are always strings.
    """
    cfg = {}
    for line in lines:
        if "=" not in line:  # ditch blank/info lines
            continue
        else:
            parts = [
                x.strip() for x in line.split("=", maxsplit=1)
            ]  # maxsplit handles '=' in values
            if len(parts) != 2:
                raise errors.AnsibleFilterError(
                    f"line {line} cannot be split into key=value"
                )
            k, v = parts
            small_v = v.lower()
            if small_v == "(null)":
                v = None
            elif small_v == "n/a":
                v = None
            elif small_v == "no":
                v = False
            elif small_v == "yes":
                v = True
            cfg[k] = v
    return cfg


class FilterModule(object):
    def filters(self):
        return {
            "config2dict": config2dict,
        }
