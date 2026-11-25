from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
  name: slurmd_topology
  short_description: Convert C(slurmd -C) output to a dict
  version_added: "3.22.0"
  description:
    - Convert the output lines of C(slurmd -C) to a dict of the C(key=value) tokens on its C(NodeName=) line.
    - V(CPUs), V(Boards), V(SocketsPerBoard), V(CoresPerSocket), V(ThreadsPerCore) and V(RealMemory) are
      converted to integers; all other values remain strings.
    - Returns an empty dict when there is no C(NodeName=) line.
  positional: value
  options:
    value:
      description:
        - Lines from C(slurmd -C) output.
      type: list
      elements: str
      required: true
"""

EXAMPLES = r"""
- name: Probe node hardware
  ansible.builtin.command: slurmd -C --parameters=numa_node_as_socket
  register: slurmd_output

- name: Convert output to dict
  ansible.builtin.set_fact:
    slurmd_topology: "{{ slurmd_output.stdout_lines | clip.hpc.slurmd_topology }}"
  # NodeName=n1 CPUs=192 Boards=1 SocketsPerBoard=2 ... returns
  # {'NodeName': 'n1', 'CPUs': 192, 'Boards': 1, 'SocketsPerBoard': 2, ...}
"""

RETURN = r"""
  _value:
    description: Dictionary of the node's hardware parameters.
    type: dict
"""

INT_KEYS = frozenset(
    {
        "CPUs",
        "Boards",
        "SocketsPerBoard",
        "CoresPerSocket",
        "ThreadsPerCore",
        "RealMemory",
    }
)


def slurmd_topology(lines):
    """Convert the output lines of `slurmd -C` to a dict.

    Only the first line starting with NodeName= carries the hardware tokens;
    the UpTime= line that follows is ignored.
    """
    topology = {}
    for line in lines:
        if not line.startswith("NodeName="):
            continue
        for token in line.split():
            key, sep, value = token.partition("=")
            if not sep:
                continue
            if key in INT_KEYS:
                try:
                    value = int(value)
                except ValueError:
                    pass
            topology[key] = value
        break
    return topology


class FilterModule(object):
    def filters(self):
        return {
            "slurmd_topology": slurmd_topology,
        }
