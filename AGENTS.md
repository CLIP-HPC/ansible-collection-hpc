# Ansible Project — Agency Configuration

This project uses the [agency](https://github.com/vbc-it/agency) framework for AI assistant configuration, mounted as a git submodule at `.agency/`.

## Rule sources

- **Organization-wide**: `.agency/rules/global/*.md` — coding standards, security policy, git conventions
- **Ansible team**: `.agency/rules/team/ansible/*.md` — Ansible-specific standards
- **Project-local**: `.github/instructions/*.instructions.md` — this project's overrides and conventions

## Available skills

Skills from `.agency/skills/` can be referenced in prompts:
- `code-review` — structured audit against organization rules
- `ansible-review` — review Ansible changes for safety, idempotency, and validation gaps
- `ansible-change-plan` — plan Ansible changes by repo shape, blast radius, and validation scope
- `open-pr` — open a PR with conventional format

## Customization

- Add project-specific instructions as new `.instructions.md` files in `.github/instructions/`.
- Instruction files use YAML frontmatter with `applyTo` for file scoping.
- Edit the commands in `.github/copilot-instructions.md` to match your actual build/test tooling.
