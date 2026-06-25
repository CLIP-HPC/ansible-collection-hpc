---
applyTo: "**/*"
---

## When writing Ansible code

- First classify the repository shape: collection, standalone role, operations/playbook, or execution environment.
- Follow patterns established in the existing codebase.
- Use FQCN modules, clear task names, and handlers.
- Keep playbooks idempotent and safe to re-run.
- Use Vault for secrets and privilege escalation sparingly.

## When reviewing Ansible changes

- First classify the repository shape — do not force collection-only conventions onto playbook repos.
- Check for idempotency and safe re-runs.
- Verify FQCN module usage.
- Check shell/command usage is justified.
- Verify handlers for service restarts.
- Assess inventory, group_vars, host_vars, dependency, and base-image blast radius.
- Review secret handling and privilege escalation.
- Verify validation coverage (`ansible-lint`, syntax check, check mode, Molecule where applicable).
- Separate blocking issues from suggestions.

## When documenting RFC changes

- Read the Jira RFC issue (title, description, comments) to understand scope.
- Read git commits and PR diffs to extract what was actually changed.
- Read the relevant playbooks, roles, and inventory for exact steps and config.
- Check whether a Confluence RFC page already exists (via Jira remote links).
- Create or update the Confluence page following the RFC page template in `.agency/rules/team/change-management/rfc-docs.md`.
- Create the Jira → Confluence remote link if one does not exist.
- Use checkboxes for procedural steps, fenced code blocks for all commands and config.
- Do not edit code files while in documentation mode.
