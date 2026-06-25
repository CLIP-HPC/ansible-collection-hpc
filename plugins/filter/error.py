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
  name: error
  short_description: Raise an error if a condition is not true
  version_added: "1.0.0"
  description:
    - Raise an C(AnsibleFilterError) with the given message if the condition evaluates to false.
    - Useful for asserting invariants in Jinja2 expressions.
  positional: value, msg
  options:
    value:
      description:
        - The condition to evaluate. If false, an error is raised.
      type: raw
      required: true
    msg:
      description:
        - The error message to raise when the condition is false.
      type: str
      required: true
"""

EXAMPLES = r"""
- name: Assert that a variable is defined
  ansible.builtin.debug:
    msg: "{{ my_var | clip.hpc.error('my_var must be set') }}"
"""

RETURN = r"""
  _value:
    description: Returns the original value unchanged if the condition is true.
    type: raw
"""

from ansible import errors


def error(condition, msg):
    """Raise an error if condition is not True"""

    if not condition:
        raise errors.AnsibleFilterError(msg)
