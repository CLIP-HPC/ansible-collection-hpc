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

# NB: To test this from the repo root run:
#   ansible-playbook -i tests/inventory -i tests/inventory-mock-groups tests/filter.yml

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
  name: hostlist_expression
  short_description: Group hostnames using Slurm hostlist expression format
  version_added: "1.0.0"
  description:
    - Group a list of hostnames using Slurm's hostlist expression format.
    - Hostnames with a common prefix and sequential numeric suffixes are grouped
      into a range expression (e.g. C(dev-foo-[00,04-05,3])).
    - The output does not guarantee the same ordering as C(scontrol hostlist),
      but passing the output to C(scontrol hostnames) returns the same hosts.
  positional: value
  options:
    value:
      description:
        - List of hostnames to group.
      type: list
      elements: str
      required: true
"""

EXAMPLES = r"""
- name: Build Slurm hostlist expression from compute group
  ansible.builtin.debug:
    msg: "{{ groups['compute'] | clip.hpc.hostlist_expression }}"
  # Returns e.g. ['dev-foo-[00,04-05,3]', 'dev-compute-[000-001]', 'my-random-host']
"""

RETURN = r"""
  _value:
    description: List of Slurm hostlist expressions.
    type: list
    elements: str
"""

import re

# Pattern to match a hostname with numerical ending
_pattern = re.compile(r"^(.*\D(?=\d))(\d+)$")


def _group_numbers(numbers):
    units = []
    ints = [int(n) for n in numbers]
    lengths = [len(n) for n in numbers]
    # sort numbers by int value and length:
    ints, lengths, numbers = zip(*sorted(zip(ints, lengths, numbers)))
    prev = min(ints)
    for i, v in enumerate(sorted(ints)):
        if v == prev + 1:
            units[-1].append(numbers[i])
        else:
            units.append([numbers[i]])
        prev = v
    return ",".join(
        ["{}-{}".format(u[0], u[-1]) if len(u) > 1 else str(u[0]) for u in units]
    )


def hostlist_expression(hosts):
    """Group hostnames using Slurm's hostlist expression format.

    E.g. with an inventory containing:

        [compute]
        dev-foo-00 ansible_host=localhost
        dev-foo-3  ansible_host=localhost
        my-random-host
        dev-foo-04 ansible_host=localhost
        dev-foo-05 ansible_host=localhost
        dev-compute-000 ansible_host=localhost
        dev-compute-001 ansible_host=localhost

    Then "{{ groups[compute] | hostlist_expression }}" will return:

        ['dev-foo-[00,04-05,3]', 'dev-compute-[000-001]', 'my-random-host']

    NB: This does not guranteed to return parts in the same order as `scontrol hostlist`,
    but its output should return the same hosts when passed to `scontrol hostnames`.
    """

    results = {}
    unmatchable = []
    for v in hosts:
        m = _pattern.match(v)
        if m:
            prefix, suffix = m.groups()
            r = results.setdefault(prefix, [])
            r.append(suffix)
        else:
            unmatchable.append(v)
    return [
        "{}[{}]".format(k, _group_numbers(v)) for k, v in results.items()
    ] + unmatchable


class FilterModule(object):
    def filters(self):
        return {
            "hostlist_expression": hostlist_expression,
        }
