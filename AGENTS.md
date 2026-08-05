# Ansible Project — Agency Configuration

This project uses the [agency](https://github.com/vbc-it/agency) framework for AI assistant configuration, mounted as a git submodule at `.agency/`.

## Rule sources

- **Organization-wide**: `.agency/rules/global/*.md` — coding standards, security policy, git conventions, CI/CD, agent operating contract
- **Ansible team**: `.agency/rules/team/ansible/*.md` — Ansible-specific standards (start from `index.md`, the always-on router; load role/playbook/collection/execution-environment/Molecule guidance only when the task needs it)
- **Project-local**: `.github/instructions/*.instructions.md` — this project's overrides and conventions

## The `.agency` submodule

- Treat `.agency/` as an external, upstream-maintained repository: never edit files inside it directly.
- `.agency` supplies generic, organization-wide and Ansible-domain-wide defaults. Project-local docs
  (this file, `.github/instructions/*.instructions.md`) are the project-specific policy authority:
  where a project-local rule is more specific than or differs from `.agency`, the project-local rule wins.
- To check for or apply an update to the pinned submodule revision, use the `check-agency-update`
  skill — it reports the available revision and requires explicit confirmation before changing
  anything. Do not run `git submodule update --remote` (or an equivalent checkout/commit) without
  that confirmation step.
- Follow the agent operating contract in `.agency/rules/global/agent-behavior.md` for every change:
  make the smallest in-scope change, run relevant validation, and treat destructive, external,
  costly, irreversible, or scope-expanding actions as requiring explicit confirmation first.
- For formal change reviews, apply `.agency/rules/team/ansible/review-checklist.md` (used by the
  `ansible-review` skill) in addition to this repository's own conventions.

## Available skills

Skills from `.agency/skills/` can be referenced in prompts. Curated for this repo's day-to-day work:
- `ansible-review` — review Ansible changes for safety, idempotency, and validation gaps
- `ansible-change-plan` — plan Ansible changes by repo shape, blast radius, and validation scope
- `code-review` — structured audit against organization rules
- `open-pr` — open a PR with conventional format
- `check-agency-update` — check whether the `.agency` submodule pin has an available update

The full skill set (`.agency/skills/{tactical,review,generation,meta}/`) covers additional workflows
— issue filing, security scanning/audits, README/changelog/docs generation, accessibility review,
cross-model PR review, and agency's own maintenance skills — reference any of them by name when the
task fits.

## Customization

- Add project-specific instructions as new `.instructions.md` files in `.github/instructions/`.
- Instruction files use YAML frontmatter with `applyTo` for file scoping.
- Edit the commands in `.github/copilot-instructions.md` to match your actual build/test tooling.
