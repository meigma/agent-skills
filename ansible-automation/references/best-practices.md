# Ansible Best Practices

Use these rules to bias toward modern, software-engineered Ansible stacks.

## 1. Re-ground on the current stable release first

- Treat stable Ansible docs as canonical, not search-engine snippets.
- For this skill revision, assume `ansible` 13.5.0 and `ansible-core` 2.20.4 unless the repo or
  user explicitly targets something else.
- Use the newest stable Ansible line as the authoring and linting baseline, then check
  compatibility with any older deployed runtime the repo still has to support.
- If you inherit older content, read the relevant porting guides before editing behavior.

## 2. Make the runtime reproducible

- Prefer an `execution-environment.yml` for shared, CI-driven, or controller-bound automation.
- Treat the control node as part of the system, not an untracked personal workstation detail.
- Keep `ansible.cfg`, collection requirements, Python dependencies, and system dependencies under
  version control.

## 3. Prefer modules over shell commands

- Reach for the most specific module that models the desired end state.
- Use `ansible.builtin.command` only when no better module exists.
- Use `ansible.builtin.shell` only when you actually need shell semantics such as pipes, redirects,
  or expansion.
- If you must use `command` or `shell`, add `changed_when`, `failed_when`, `creates`, or `removes`
  so the task still behaves like declarative automation.

## 4. Use FQCNs and canonical names everywhere

- Write `ansible.builtin.copy`, not `copy`.
- Use fully qualified names for third-party content too.
- Do not rely on the `collections:` keyword as an implicit namespace mechanism.
- Favor canonical module names over legacy aliases.

## 5. Write for idempotence, not one-shot success

- A task is not done when it works once; it is done when repeated runs converge with correct change
  reporting.
- Use `state: present`, `state: started`, and other declarative states by default.
- Reserve `state: latest` for deliberate upgrade paths, and add guardrails such as `update_only` or
  `only_upgrade` where the module supports them.
- Prefer handlers over ad hoc `when: result.changed` follow-up tasks.

## 6. Keep orchestration separate from implementation

- Playbooks should describe host targeting, role ordering, and top-level orchestration.
- Roles should implement focused behavior with clear inputs and outputs.
- Split large roles into smaller task files only when it improves readability; if you do, keep
  task names easy to trace back to their source file.
- Promote shared plugins, roles, and modules into collections when reuse grows beyond one repo.

## 7. Treat variables as an interface

- Put each variable in one intentional home.
- Use inventory for geography, environment, and host-specific behavior.
- Use `roles/<role>/defaults/main.yml` for overridable role inputs.
- Use `roles/<role>/vars/main.yml` only for values you deliberately want to be hard to override.
- Pass role parameters explicitly in the play when you need clarity at the call site.
- Avoid turning `set_fact` into a global mutable state store.

## 8. Put data differences in data, not in tangled conditionals

- Separate OS- or environment-specific values into vars files and templates selected by facts.
- Keep templates simple; avoid huge conditional trees inside a single Jinja file.
- Use raw expressions in `when`, `failed_when`, and `changed_when`. Do not wrap them in `{{ }}`.
- Cast non-boolean variables with `| bool` when a conditional expects boolean intent.

## 9. Pin and verify external content

- Store collection dependencies in `requirements.yml` or `collections/requirements.yml`.
- Constrain collection versions instead of pulling arbitrary latest releases on every run.
- Pin system and Python dependencies in execution environments or other build inputs.
- Prefer signed or otherwise verifiable collection sources when your distribution path supports it.

## 10. Protect secrets and sensitive output

- Use Ansible Vault for encrypted files and variables.
- Add `no_log: true` anywhere task output could reveal secrets, especially in loops.
- Disable `diff` for secret-bearing file tasks with `diff: false`.
- Keep secrets out of plaintext inventory, committed vars files, and verbose debug output.

## 11. Design for unattended execution

- Avoid `vars_prompt` and `pause` in normal automation stacks.
- Keep the non-interactive path first-class so the same code can run locally, in CI, and in a
  controller.
- If a task must behave differently in check mode, make that explicit with `ansible_check_mode` or
  `check_mode: true/false`.

## 12. Enforce a quality gate

- Run `ansible-playbook --syntax-check` before deeper validation.
- Run `ansible-playbook --check --diff` against a safe slice before trusting behavioral changes.
- Run `ansible-lint` with the highest viable profile. The goal state is `shared` or `production`.
- Keep CI wired to the same runtime and lint configuration you expect from humans.

## Preferred build sequence

1. Decide the target runtime and make it explicit.
2. Model environments and inventories.
3. Pin collections and external dependencies.
4. Build thin playbooks and focused roles.
5. Add secret handling with Vault before real credentials appear.
6. Add syntax check, check mode, diff mode, and ansible-lint to CI.

## Source anchors

- Stable Ansible docs: <https://docs.ansible.com/projects/ansible/latest/>
- Sample setup: <https://docs.ansible.com/projects/ansible/latest/tips_tricks/sample_setup.html>
- Variables and precedence:
  <https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_variables.html>
- Conditionals:
  <https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_conditionals.html>
- Check mode and diff mode:
  <https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html>
- Vault guide: <https://docs.ansible.com/projects/ansible/latest/vault_guide/index.html>
- Collections install and requirements:
  <https://docs.ansible.com/projects/ansible/latest/collections_guide/collections_installing.html>
- Execution Environments:
  <https://docs.ansible.com/projects/ansible/latest/getting_started_ee/index.html>
- ansible-builder definition:
  <https://docs.ansible.com/projects/builder/en/latest/definition/>
- ansible-lint usage and rules: <https://docs.ansible.com/projects/lint/>
