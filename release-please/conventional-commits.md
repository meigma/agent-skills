# Conventional Commits Reference

Release Please derives version bumps and changelog entries from Conventional Commits.

## Commit Format

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Release-Relevant Types

| Type | Effect |
|------|--------|
| `fix` | Patch release |
| `feat` | Minor release |
| `type!` | Major release |
| `BREAKING CHANGE:` footer | Major release |

Release Please also recognizes `feature` as a feature type in the default versioning strategy.

## Examples

### Feature

```text
feat(auth): add OIDC login support
```

### Fix

```text
fix(parser): handle empty input
```

### Breaking Change with `!`

```text
feat!: replace v1 API with v2 API
```

### Breaking Change with Footer

```text
feat(config): redesign configuration loading

BREAKING CHANGE: The old top-level server key was removed.
```

### Issue Reference

```text
fix(cache): avoid stale reads after invalidation

Closes #123
```

## Pre-1.0.0 Behavior

Current default behavior still follows the default semver strategy:

- breaking changes bump **major**
- features bump **minor**
- fixes bump **patch**

You only get different `<1.0.0` behavior when you opt into these config flags:

```json
{
  "bump-minor-pre-major": true,
  "bump-patch-for-minor-pre-major": true
}
```

With those flags enabled:

- breaking changes bump **minor** instead of major
- features bump **patch** instead of minor

## Additional Types

These types are useful for changelog organization, but they do not change the default release type unless you customize changelog behavior:

- `docs`
- `perf`
- `refactor`
- `revert`
- `build`
- `ci`
- `test`
- `chore`
- `style`

## Scopes

Scopes make changelogs easier to read:

```text
feat(api): add rate limiting
fix(ui): stop layout shift in modal
docs(readme): update installation instructions
```

Use scopes that match the part of the system users will recognize:

- package names
- modules
- subsystems
- public surfaces

## `Release-As:` Override

When you need an exact next version, use a `Release-As:` footer in the commit body:

```text
chore: cut the next stable release

Release-As: 2.0.0
```

Prefer this over config-level `release-as`.

## Commit Overrides in Release PRs

If you need to adjust generated release notes without rewriting history, add overrides to the release PR body:

```markdown
BEGIN_COMMIT_OVERRIDE
- feat: custom feature description for release notes
- fix: custom fix description for release notes
END_COMMIT_OVERRIDE
```

## Merge Strategy Guidance

Squash merges are strongly recommended because they keep release notes and changelog entries easier to control. They are not required. Release Please also works with merge commits, but changelog quality depends more heavily on how commits are written.

## Canonical References

- https://github.com/googleapis/release-please
- https://www.conventionalcommits.org/en/v1.0.0/
- https://github.com/googleapis/release-please/blob/main/docs/manifest-releaser.md
