# Ansible project

Ansible automation for configuration management, deployment, and infrastructure operations.

## Agent definition

#file:.agency/agents/stack/ansible-coder.md

## Commands

- `ansible-lint` — lint playbooks and roles
- `ansible-playbook --syntax-check playbook.yml` — syntax validation
- `ansible-playbook -C playbook.yml --diff` — dry-run with diffs
- `molecule test` — run molecule scenarios for roles
- `molecule converge` — converge (test a single scenario)
- Run `ansible-lint` before every commit.

## Conventions

- Use FQCN for all modules (e.g., `ansible.builtin.copy:` not `copy:`).
- All tasks must have a clear `name:`.
- Use `ansible.builtin.shell` / `command` only when no dedicated module exists.
- Use handlers for service restarts triggered by config changes.
- Use `check_mode:` for tasks that should run in dry-run mode.
- Never hardcode secrets. Use Ansible Vault or external secrets lookup.
- For collections: follow collection structure with `galaxy.yml`, `meta/runtime.yml`.
- For playbooks: prefer flat playbooks over deep role nesting unless roles are shared.
- For execution environments: pin all deps, treat base image changes as high blast radius.
- For inventories: changes to group vars, host vars, or inventory source have wide impact.
- Distinguish collection repos, standalone role repos, playbook/ops repos, and EE repos.

## File structure

Varies by repo shape. See `.agency/rules/team/ansible/collection-structure.md` and `.agency/rules/team/ansible/playbook-patterns.md`.

## Available skills

Skills from `.agency/skills/` can be referenced in prompts:
- `code-review` — structured audit against organization rules
- `ansible-review` — review Ansible changes for safety, idempotency, and validation gaps
- `ansible-change-plan` — plan Ansible changes by repo shape, blast radius, and validation scope
- `open-pr` — open a PR with conventional format
