from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
  name: slurm_slices
  short_description: Map nodes to the Slurm partition slices that list them
  version_added: "3.14.0"
  description:
    - Collect the C(nodes) of every partition in O(slurm_partitions) and map each node to the partitions
      listing it, split into exclusive and shared slices.
    - C(nodes) is a list of node names or Slurm hostlist expressions (e.g. C(cbe-c3-[13-18])), or a single
      such string. Names are reduced to the short hostname.
    - A slice is exclusive unless the partition sets C(exclusive=false).
  positional: value
  options:
    value:
      description:
        - The partition definitions, as in C(slurm_partitions).
      type: list
      elements: dict
      required: true
"""

EXAMPLES = r"""
- name: Show which slices each node belongs to
  ansible.builtin.debug:
    msg: "{{ slurm_partitions | clip.hpc.slurm_slices }}"
  # With partitions [{name: grid, nodes: 'cbe-c3-[13-14]'}, {name: debug, nodes: [cbe-c3-14], exclusive: false}]
  # returns {'cbe-c3-13': {'exclusive': ['grid'], 'shared': []},
  #          'cbe-c3-14': {'exclusive': ['grid'], 'shared': ['debug']}}
"""

RETURN = r"""
  _value:
    description: Short node name mapped to the names of its exclusive and shared slices.
    type: dict
"""

import re

from ansible.errors import AnsibleFilterError

_bracket = re.compile(r"^(.*?)\[([^\[\]]+)\](.*)$")


def _split_top_level(expr):
    parts, depth, current = [], 0, ""
    for c in expr:
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
        if c == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += c
    parts.append(current)
    return [p.strip() for p in parts if p.strip()]


def _expand_range(token, expr):
    if "-" not in token:
        return [token]
    start, end = token.split("-", 1)
    if not (start.isdigit() and end.isdigit()) or int(start) > int(end):
        raise AnsibleFilterError("invalid range '%s' in hostlist '%s'" % (token, expr))
    width = len(start) if start.startswith("0") else 0
    return [str(i).zfill(width) for i in range(int(start), int(end) + 1)]


def _expand(expr):
    m = _bracket.match(expr)
    if not m:
        return [expr]
    prefix, ranges, rest = m.groups()
    hosts = []
    for token in ranges.split(","):
        for n in _expand_range(token.strip(), expr):
            hosts.extend(_expand(prefix + n + rest))
    return hosts


def expand_hostlist(nodes):
    items = [nodes] if isinstance(nodes, str) else list(nodes or [])
    hosts = []
    for item in items:
        for part in _split_top_level(str(item)):
            hosts.extend(h.split(".")[0] for h in _expand(part))
    return hosts


def slurm_slices(partitions):
    slices = {}
    for partition in partitions or []:
        if "nodes" not in partition:
            continue
        kind = "exclusive" if partition.get("exclusive", True) else "shared"
        for node in expand_hostlist(partition["nodes"]):
            entry = slices.setdefault(node, {"exclusive": [], "shared": []})
            if partition["name"] not in entry[kind]:
                entry[kind].append(partition["name"])
    return slices


class FilterModule(object):
    def filters(self):
        return {
            "slurm_slices": slurm_slices,
        }
