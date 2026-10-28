# clip.hpc Ansible collection

`clip.hpc` is an Ansible Collection (namespace `clip`, name `hpc`) with the roles that deploy the CBE HPC cluster. Roles live under `roles/` (`beegfs`, `dell_dsu`, `doca`, `multirail`, `rdma_exporter`, `rocev2`, `slurm`, `smartctl_exporter`); each role's `README.md` documents its variables, and the top-level `README.md` lists the roles.

## Environment setup

- Python is pinned via `.python-version` (3.11); dev dependencies (`ansible-core`, `molecule`, `ansible-lint`, `molecule-plugins[vagrant]`) are declared in `pyproject.toml` and locked in `uv.lock`.
- `.envrc` uses `direnv` + `uv` (creates `.venv` and runs `uv sync`) and sources `ansible.env`, which sets `ANSIBLE_ROLES_PATH`, `ANSIBLE_LIBRARY`, and `ANSIBLE_FILTER_PLUGINS` for Molecule. On Apple Silicon it also sets the Vagrant/VirtualBox variables (`VAGRANT_PROVIDER`, AlmaLinux 9/10 boxes, `DISABLE_SLURM_JOB_CONTAINER`). Without direnv, run `uv sync` and source `ansible.env` manually.
- `flake.nix` with `nix/ansible-2_15/` and `nix/ansible-2_20/` provides Nix environments for the oldest and newest supported ansible-core.

## Commands

- Lint: `ansible-lint` (also via pre-commit together with `black`, `shellcheck`, and standard `pre-commit-hooks`); run all hooks with `pre-commit run --all-files`.
- Syntax check a playbook: `ansible-playbook --syntax-check playbooks/<playbook>.yml`
- Dry run with diff: `ansible-playbook -C <playbook>.yml --diff`
- Molecule scenarios live under `extensions/molecule/<role>/<platform>/` (e.g. `slurm/rhel9`, `slurm/rhel10`, `beegfs/rhel10`, `doca/rhel9`), not in `roles/<role>/molecule/`, and share `extensions/molecule/config.yml` (Galaxy requirements from `tests/requirements.yml`) and the inventory in `extensions/molecule/inventory/`. The default test sequence includes an idempotence step.
- CI (`.github/workflows/ci.yml`) delegates to the reusable workflow `vbc-it/github-action-workflows/.github/workflows/ansible-collection.yml` on a self-hosted runner with `molecule_env_file: ansible.env`, and publishes to Automation Hub on success.
- Run `ansible-lint` before every commit.

## Conventions

- This is a **collection** repository; apply collection-shaped guidance.
- Use FQCN for all modules; every task needs a clear `name:`; use handlers for service restarts; never hardcode secrets (use Ansible Vault or an external secrets lookup).
- Role variables are prefixed with the role name (e.g. `beegfs_enable_quota`, `slurm_*`).
- Releases: each change that ships bumps `version` in `galaxy.yml` and adds a `vX.Y.Z` section to `CHANGELOG.rst` (one bullet per change, prefixed with the role name, and **Breaking:** where applicable). `meta/runtime.yml` sets `requires_ansible: '>=2.15.0'`.
- Collection plugins live in `plugins/filter/` (`config2dict`, `dict2parameters`, `hostlist_expression`, `slurm_slices`, …) and `plugins/modules/slurm.py`; standalone playbooks in `playbooks/` (`dell_dsu_report.yml`, `dell_dsu_update.yml`).
- Project-local docs (this file, `.github/instructions/*.instructions.md`) are the project-specific policy authority: where a project-local rule is more specific than or differs from the agency skills, the project-local rule wins.
- When writing RFC or infrastructure documentation for changes here, prioritise reading playbooks, roles, and inventory files for technical detail.

<!-- agency:managed:start source=templates/ansible/AGENTS.md.tmpl -->
## Required routing

Pushing, force-pushing, opening or commenting on a PR, merging, releasing, and deploying are external actions. A request to do one is not the confirmation: state the exact command, target, and effect, and wait for a yes before running it.

Use the `vbc-standards` skill before acting on a task.

Use the `vbc-ansible-standards` skill before changing Ansible content.

## Skills

When a task matches one of these, use the skill:

- `ansible-review` — review Ansible changes for safety and best practices
- `ansible-change-plan` — plan Ansible changes by blast radius
- `code-review` — structured audit against organization rules
- `open-pr` — open a PR with conventional format
- `agentgateway-mcp` — query internal metrics, logs, inventory, and fabric state read-only

Use other skills only when their trigger matches the task.
<!-- agency:managed:end -->

## Project-local customization

Keep this repository's actual commands and facts here; organization and domain behavior comes from the agency plugins (`it`, `it-infra`, `it-ansible`), enabled in `.claude/settings.json`. Add a nested `AGENTS.md` only for subtree-specific facts or routing, never to copy agency skill content.
