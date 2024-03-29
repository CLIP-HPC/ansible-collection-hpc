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

# pylint: disable=consider-using-f-string

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible import errors
from ansible.module_utils.six import iteritems
# NOTE: jinja2 3.1.0 dropped contextfilter in favour of pass_context.
try:
    from jinja2 import pass_context
except ImportError:
    from jinja2 import contextfilter as pass_context
import re

# Pattern to match a hostname with numerical ending
pattern = re.compile(r'^(.*\D(?=\d))(\d+)$')


def _get_hostvar(context, var_name, inventory_hostname=None):
    if inventory_hostname is None:
        namespace = context
    else:
        if inventory_hostname not in context['hostvars']:
            raise errors.AnsibleFilterError(
                "Inventory hostname '%s' not in hostvars" % inventory_hostname)
        namespace = context["hostvars"][inventory_hostname]
    return namespace.get(var_name)


@pass_context
def group_hosts(context, group_names):
    return {g: _group_hosts(context["groups"].get(g, []))
            for g in sorted(group_names)}


def _group_hosts(hosts):
    results = {}
    unmatchable = []
    for v in hosts:
        m = pattern.match(v)
        if m:
            prefix, suffix = m.groups()
            r = results.setdefault(prefix, [])
            r.append(int(suffix))
        else:
            unmatchable.append(v)
    return ['{0}[{1}]'.format(k, _group_numbers(v))
            for k, v in iteritems(results)] + unmatchable


def _group_numbers(numbers):
    units = []
    prev = min(numbers)
    for v in sorted(numbers):
        if v == prev + 1:
            units[-1].append(v)
        else:
            units.append([v])
        prev = v
    return ','.join(['{0}-{1}'.format(u[0], u[-1])
                    if len(u) > 1 else str(u[0]) for u in units])


class FilterModule(object):

    def filters(self):
        return {
            'group_hosts': group_hosts
        }
