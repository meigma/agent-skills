# Ansible Anti-Patterns

Reject these patterns even if they appear frequently in search results, old blog posts, or low-bar
internal repos.

## 1. Short module names and implicit namespaces

Bad:

- `copy:`
- `service:`
- a top-level `collections:` block to make short names work

Prefer:

- `ansible.builtin.copy:`
- `ansible.builtin.service:`
- explicit FQCNs for all third-party content

Why this is bad:

- It hides provenance, increases ambiguity, and bakes legacy 2.9 migration patterns into new code.

## 2. Shell-heavy playbooks

Bad:

- `shell: apt-get update`
- `shell: systemctl restart nginx`
- `shell: sed -i ...`

Prefer:

- package, service, template, lineinfile, file, user, git, uri, unarchive, and other specific
  modules
- `ansible.builtin.command` only when no declarative module exists

Why this is bad:

- Shell tasks are slower, less portable, harder to lint, and usually weaker at reporting change.

## 3. Command or shell tasks with no idempotence contract

Bad:

- arbitrary commands with no `changed_when`, `failed_when`, `creates`, or `removes`

Prefer:

- explicit change and failure rules
- declarative modules first

Why this is bad:

- The playbook may "work" while lying about whether it changed anything.

## 4. `state: latest` as the default install strategy

Bad:

- package installs that always chase the newest version
- upgrades mixed into normal converge runs without guardrails

Prefer:

- `state: present`
- explicit versions where reproducibility matters
- deliberate upgrade tasks with `update_only` or `only_upgrade` when supported

Why this is bad:

- It turns converge runs into surprise upgrade runs and makes incidents harder to reproduce.

## 5. `ignore_errors: true` as a blanket escape hatch

Bad:

- swallowing failures without recording or evaluating them

Prefer:

- `register`
- `failed_when`
- `ignore_errors: "{{ ansible_check_mode }}"`

Why this is bad:

- It hides real breakage and produces misleading runs.

## 6. `when: "{{ ... }}"` and stringly-typed conditionals

Bad:

- nested Jinja in `when`, `changed_when`, or `failed_when`
- relying on `"yes"` or `"no"` strings without `| bool`

Prefer:

- raw conditional expressions
- explicit boolean casting where needed

Why this is bad:

- It is a known Ansible anti-pattern and often behaves differently than the author intends.

## 7. Giant playbooks with copied task blocks

Bad:

- hundreds of lines in `site.yml`
- near-duplicate task blocks per environment or per operating system

Prefer:

- thin playbooks
- focused roles
- vars files and templates selected by facts or inventory

Why this is bad:

- It destroys reuse, increases drift, and makes review harder than it needs to be.

## 8. Variable-precedence roulette

Bad:

- the same variable name defined in inventory, group vars, host vars, play vars, role vars, and
  extra vars with no deliberate reason
- stuffing everything into `group_vars/all`

Prefer:

- one intentional home per variable
- inventory for environment data
- role defaults for overridable role inputs
- role vars only for truly fixed internal values

Why this is bad:

- The code becomes hard to reason about because behavior depends on hidden override order.

## 9. Treating `set_fact` as a global datastore

Bad:

- pushing configuration into `set_fact` early and reading it everywhere later
- cross-role coupling through ad hoc facts

Prefer:

- stable inputs from inventory, role defaults, role params, or vars files
- `set_fact` only for derived runtime values that genuinely need to exist during execution

Why this is bad:

- It creates hidden dependencies and stateful playbooks that are hard to test.

## 10. Secrets in plaintext or leaked in output

Bad:

- unencrypted passwords in inventory or vars files
- loops over secrets without `no_log: true`
- diffs of secret-bearing templates

Prefer:

- Vault-encrypted files or values
- `no_log: true`
- `diff: false` where output would expose sensitive data

Why this is bad:

- It turns routine automation runs into a credential disclosure channel.

## 11. Change-triggered tasks implemented as normal tasks

Bad:

- `when: result.changed` chains instead of handlers

Prefer:

- `notify` and `handlers`

Why this is bad:

- It obscures intent and fights the execution model Ansible already provides.

## 12. Interactive automation

Bad:

- `vars_prompt`
- `pause`
- workflows that require a human terminal to complete a normal run

Prefer:

- unattended, parameterized execution
- explicit CI-safe defaults

Why this is bad:

- It breaks controllers, CI, and repeatable operations.

## 13. Floating dependencies everywhere

Bad:

- unbounded Galaxy installs
- unpinned base images
- ad hoc control-node packages installed manually on laptops

Prefer:

- versioned requirements files
- execution environments or otherwise explicit runtime definitions
- documented and reproducible dependency updates

Why this is bad:

- The same repo stops meaning the same thing from one machine or week to the next.

## 14. Cleverness over traceability

Bad:

- deeply nested Jinja
- over-abstracted includes and imports used without understanding their execution differences
- magic variable derivations that save lines but lose clarity

Prefer:

- obvious data flow
- simple task files
- deliberate use of `import_*` versus `include_*`

Why this is bad:

- Reviewers and future maintainers lose the ability to predict behavior safely.

## Refusal heuristic

If a snippet looks like one of these patterns, do not polish it. Replace it with a structure that:

1. uses current syntax
2. makes provenance explicit
3. reports change honestly
4. runs unattended
5. can be validated in check mode, diff mode, and ansible-lint

## Source anchors

- Stable Ansible docs: <https://docs.ansible.com/projects/ansible/latest/>
- Variables and precedence:
  <https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_variables.html>
- Conditionals:
  <https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_conditionals.html>
- Check mode and diff mode:
  <https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html>
- Vault guide: <https://docs.ansible.com/projects/ansible/latest/vault_guide/index.html>
- ansible-lint rule set: <https://docs.ansible.com/projects/lint/rules/>
