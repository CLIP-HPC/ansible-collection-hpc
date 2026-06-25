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
  name: dict2parameters
  short_description: Convert a dict to a C(key=value) parameter string
  version_added: "1.0.0"
  description:
    - Convert a dict into a string in C(k1=v1 k2=v2 ...) format suitable for use as command-line parameters.
  positional: value
  options:
    value:
      description:
        - The dict to convert.
      type: dict
      required: true
"""

EXAMPLES = r"""
- name: Build parameter string from dict
  ansible.builtin.command: "some_command {{ my_dict | clip.hpc.dict2parameters }}"
"""

RETURN = r"""
  _value:
    description: String in C(key=value) format with space-separated pairs.
    type: str
"""


def dict2parameters(d):
    """Convert a dict into a str in 'k1=v1 k2=v2 ...' format"""
    parts = ["%s=%s" % (k, v) for k, v in d.items()]
    return " ".join(parts)


class FilterModule(object):
    def filters(self):
        return {
            "dict2parameters": dict2parameters,
        }
