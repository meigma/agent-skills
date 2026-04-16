---
name: ansible-automation
description: >
  Build, review, and modernize Ansible automation stacks with a current,
  software-engineering quality bar. Use when creating or refactoring
  `ansible.cfg`, inventories, playbooks, roles, collection requirements,
  execution environments, Vault usage, or CI/linting for Ansible. Bias toward
  current Ansible docs, ansible-lint production rules, and reproducible
  dependencies, and away from shell-heavy playbooks, implicit behavior, and
  variable-precedence chaos.
---

# Ansible Automation

Use this skill as a corrective lens, not a tutorial. Assume your generic Ansible prior is
polluted by old 2.9-era snippets, shell-first playbooks, and examples that ignore idempotence,
reuse, and validation. Re-ground on current docs first, then write content that is explainable,
testable, and repeatable.

## Verified against

- `ansible` 13.5.0 (PyPI, released 2026-03-25)
- `ansible-core` 2.20.4 (PyPI, released 2026-03-23)
- Stable docs: <https://docs.ansible.com/projects/ansible/latest/>
- Current porting guide:
  <https://docs.ansible.com/projects/ansible/latest/porting_guides/porting_guide_core_2.20.html>
- ansible-lint docs and profiles: <https://docs.ansible.com/projects/lint/>
- Execution Environment docs:
  <https://docs.ansible.com/projects/ansible/latest/getting_started_ee/>
- ansible-builder 3.x definition docs:
  <https://docs.ansible.com/projects/builder/en/latest/definition/>

Ignore prereleases as a baseline unless the user explicitly asks for them. On 2026-04-15, PyPI
also showed `ansible` 14.0.0a2 and `ansible-core` 2.21.0b2; those are not the default target for
normal stack work.

## Use this skill when

- You are creating or refactoring an Ansible repo, playbook set, role library, or automation
  stack.
- You are reviewing existing Ansible code and need to raise its quality bar.
- You need guidance on modern repo layout, inventory structure, dependency management, execution
  environments, linting, or validation.
- You suspect the existing content was written around legacy conventions and needs to be re-grounded
  on current Ansible behavior.

## Source priority

1. Current stable Ansible docs under `projects/ansible/latest/`
2. Relevant `ansible-core` porting guides for the target version
3. Current ansible-lint rule docs and profiles
4. Execution Environment and ansible-builder docs for runtime reproducibility
5. The repository's own existing patterns, once they clear the quality bar
6. Memory, only after checking the above

## Version-reset workflow

Before making recommendations or edits:

1. Check the actual toolchain with `ansible --version`, `ansible-lint --version`, and
   `ansible-config dump --only-changed` when a repo already exists.
2. Treat the stable docs as canonical. ansible-lint explicitly recommends using the newest version
   of Ansible even if production runs older versions, so use the newest stable line as your
   authoring and linting baseline. Do not write to prerelease or `devel` behavior unless asked.
3. If the repo spans an older core line, read the relevant porting guides before changing syntax or
   semantics.
4. Assume short module names, `collections:` reliance, shell-heavy tasks, and global
   `ignore_errors: true` are suspect until proven necessary.
5. Prefer to make the runtime explicit with `execution-environment.yml` when the stack is shared,
   CI-driven, or controller-bound.

## Non-negotiables

1. Prefer purpose-built modules over `command` or `shell`.
2. Prefer `ansible.builtin.command` over `ansible.builtin.shell` unless shell features are
   required.
3. Use FQCNs everywhere. Do not rely on the `collections:` keyword.
4. Write for idempotence. Tasks must converge cleanly, report change accurately, and survive
   re-runs.
5. Keep playbooks thin and orchestration-oriented. Put reusable behavior in roles; graduate to
   collections when the surface area justifies it.
6. Put variables in one place based on desired override scope. Defaults go in `defaults/main.yml`;
   geography and environment data go in inventory; hard role constants belong in `vars/main.yml`
   only when you truly want them hard to override.
7. Use handlers for change-triggered follow-up work.
8. Keep secrets encrypted with Vault and suppress sensitive output with `no_log: true` and
   `diff: false` where appropriate.
9. Pin dependency versions or at least constrain them. Do not let Galaxy, pip, system packages,
   and container inputs all float implicitly.
10. Validate every stack with syntax check, check mode, diff mode, and ansible-lint.

## Default stack shape

```text
ansible.cfg
collections/
  requirements.yml
execution-environment.yml
inventories/
  production/
    hosts.yml
    group_vars/
    host_vars/
  staging/
    hosts.yml
    group_vars/
    host_vars/
playbooks/
  site.yml
  webservers.yml
  dbservers.yml
roles/
  common/
    defaults/main.yml
    handlers/main.yml
    tasks/main.yml
    templates/
    files/
  app/
.github/workflows/ansible.yml
.ansible-lint
```

Adjust the shape to the repo's actual needs, but keep these boundaries:

- inventory contains environment data
- playbooks orchestrate
- roles implement
- dependency files pin external content
- execution environments make the runtime reproducible

## Validation loop

Use this loop by default:

```bash
ansible-playbook playbooks/site.yml --syntax-check
ansible-playbook playbooks/site.yml --check --diff --limit <safe-slice>
ansible-lint --profile production
```

If `production` is too strict early in a migration, start lower and ratchet up. The target should
still be `shared` or `production` before you call the stack healthy.

## Curated notes

- [Best practices](references/best-practices.md)
- [Anti-patterns](references/anti-patterns.md)

## Maintenance checklist

Re-verify this skill whenever a new Ansible or ansible-core release lands:

1. Check PyPI for current stable `ansible` and `ansible-core`.
2. Re-open:
   - stable Ansible docs
   - current ansible-core porting guide
   - ansible-lint usage and rules
   - Execution Environment getting started guide
   - ansible-builder definition docs
3. Update any version numbers, deprecated guidance, or renamed modules.
4. Delete any recommendation that can no longer be grounded in current docs.
