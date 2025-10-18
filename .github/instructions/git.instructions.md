---
applyTo: "**/*"
description: "Use Conventional Commits v1.0.0 specification for all commit messages"
---

# Conventional Commits Specification

Follow the Conventional Commits 1.0.0 specification for all commit messages.

## Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Core Types (Spec-Required)

- **feat**: A new feature (correlates with MINOR in SemVer)
- **fix**: A bug fix (correlates with PATCH in SemVer)

## Additional Types (Recommended)

Based on Angular convention, these are commonly used:

- **build**: Build system or external dependencies (webpack, npm, etc.)
- **chore**: Maintenance tasks, no production code change
- **ci**: CI/CD configuration changes (GitHub Actions, CircleCI, etc.)
- **docs**: Documentation only changes
- **perf**: Performance improvements
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **revert**: Reverting a previous commit
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **test**: Adding or updating tests

## Specification Rules

1. **MUST** be prefixed with a type followed by optional scope, optional `!`, and REQUIRED colon and space
2. Type `feat` **MUST** be used for new features
3. Type `fix` **MUST** be used for bug fixes
4. Scope **MAY** be provided after type (noun in parentheses): `feat(parser):`
5. Description **MUST** immediately follow the colon and space
6. Body **MAY** be provided after description (one blank line after)
7. Footer(s) **MAY** be provided one blank line after body
8. Breaking changes **MUST** be indicated with `!` before `:` or `BREAKING CHANGE:` footer

## Breaking Changes

**Option 1: Use `!` in type/scope**
```
feat!: send email when product ships
feat(api)!: change response format
```

**Option 2: Use footer**
```
feat: allow config to extend other configs

BREAKING CHANGE: `extends` key now used for extending config files
```

**Option 3: Both**
```
chore!: drop Node 6 support

BREAKING CHANGE: use JavaScript features not available in Node 6
```

Breaking changes trigger MAJOR version in SemVer regardless of type.

## Examples

**Feature with scope:**
```
feat(lang): add Polish language support
```

**Fix with body:**
```
fix: prevent racing of requests

Introduce request id and reference to latest request. Dismiss
incoming responses other than from latest request.
```

**Breaking change:**
```
feat(api)!: send email to customer when product ships
```

**Multiple footers:**
```
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Reviewed-by: Z
Refs: #123
```

**Documentation:**
```
docs: correct spelling of CHANGELOG
```

**Revert:**
```
revert: let us never again speak of the noodle incident

Refs: 676104e, a215868
```

## Scopes

Use meaningful scopes for your project:
- **Component names**: `(auth)`, `(api)`, `(ui)`, `(parser)`
- **File areas**: `(models)`, `(views)`, `(tests)`, `(config)`
- **Feature areas**: `(payments)`, `(notifications)`, `(analytics)`

## Body Format

- Begin one blank line after description
- Free-form, may contain multiple paragraphs separated by blank lines
- Provides additional context about code changes

## Footer Format

- Begin one blank line after body (or description if no body)
- Follow git trailer convention
- Token followed by `: ` or ` #` separator and value
- Use `-` for multi-word tokens: `Reviewed-by`, `Acked-by`
- `BREAKING CHANGE` is exception (can use spaces)
- Common footers: `Refs`, `Reviewed-by`, `Co-authored-by`, `BREAKING CHANGE`

## Best Practices

1. **Imperative mood**: Use "add" not "added" or "adds"
2. **Lowercase**: Type and description should be lowercase
3. **No period**: Don't end description with period
4. **Be specific**: Clear, concise descriptions
5. **First line ≤ 72 chars**: Keep subject line readable
6. **One concern per commit**: Split unrelated changes
7. **Body explains why**: Not just what changed
8. **Reference issues**: Use footers like `Refs: #123`

## Co-authored Commits

```
feat(parser): add YAML support

Co-authored-by: Name <email@example.com>
Co-authored-by: Another <another@example.com>
```

## SemVer Mapping

- `fix:` → PATCH release (0.0.X)
- `feat:` → MINOR release (0.X.0)
- `BREAKING CHANGE:` or `!` → MAJOR release (X.0.0)
- Other types have no implicit SemVer effect

## Case Sensitivity

- Any casing may be used, but **be consistent**
- Best practice: lowercase for types
- Exception: `BREAKING CHANGE` must be uppercase in footers
- `BREAKING-CHANGE` is synonym of `BREAKING CHANGE`