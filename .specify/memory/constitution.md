<!--
Sync Impact Report:
- Version: Initial → 1.0.0
- Constitution created from scratch for Pomodoro Timer project
- Modified Principles: N/A (initial creation)
- Added Sections: All - Core Principles (5), Quality Gates, Development Workflow, Governance
- Removed Sections: N/A
- Templates Updated:
  ✅ .specify/templates/plan-template.md - Added Constitution Check with specific principle gates
  ✅ .specify/templates/spec-template.md - Already aligned (no changes needed)
  ✅ .specify/templates/tasks-template.md - Updated to mandate tests (was optional, now required)
  ✅ .github/prompts/speckit.tasks.prompt.md - Updated to mandate tests throughout
  ✅ .github/prompts/*.md - Verified no agent-specific references (CLAUDE, GPT, etc.)
- Follow-up TODOs: None - all placeholders resolved, all templates synchronized
-->

# Pomodoro Timer Constitution

## Core Principles

### I. Test-First Development (NON-NEGOTIABLE)

Every feature MUST follow strict TDD workflow:
- Write acceptance tests FIRST (derived from user stories)
- Get user approval on failing tests before any implementation
- Follow Red-Green-Refactor cycle rigorously
- Tests define the contract - implementation follows

**Rationale**: Tests document intent, catch regressions early, and ensure features solve the actual problem before code is written. This is especially critical in early development to establish correct patterns.

### II. Type Safety & Code Quality

All code MUST meet these non-negotiable standards:
- Type hints required on all functions (enforced by `ty`)
- Google-style docstrings required on all public interfaces (enforced by `ruff`)
- 100-character line length (enforced by `ruff`)
- Zero linting errors before commit
- Code formatted via `ruff format`

**Rationale**: Type safety catches bugs at development time. Consistent style reduces cognitive load. Documentation ensures maintainability as the project grows.

### III. Incremental & Independent Implementation

Features MUST be broken into independently testable user stories:
- Each story deliverable as standalone MVP increment
- Stories prioritized (P1, P2, P3...) by value
- Implementation validates one story completely before starting next
- Parallel work only on different stories with no shared files

**Rationale**: Incremental delivery provides early value, reduces risk, and allows course correction. Independent stories enable team parallelization without merge conflicts.

### IV. Modern Python Tooling

Project MUST use cutting-edge Python ecosystem tools:
- `uv` for all dependency management (never manual `pyproject.toml` edits)
- `ruff` for linting and formatting (single tool replaces multiple)
- `ty` for type checking
- `pytest` with coverage tracking
- Python 3.12+ features and idioms

**Rationale**: Modern tooling dramatically improves developer experience and reduces configuration overhead. `uv` eliminates dependency hell. `ruff` is 100x faster than legacy tools. Type checking prevents entire bug classes.

### V. Simplicity & YAGNI

Start simple and only add complexity when proven necessary:
- No frameworks until clearly needed (CLI-first with stdlib)
- No abstractions until pattern repeats 3+ times
- No dependencies until stdlib insufficient
- Question every "what if" scenario - implement when needed, not before

**Rationale**: Premature abstraction is the root of all evil. Simple code is readable, debuggable, and maintainable. The Pomodoro Timer should stay lean and focused.

## Quality Gates

### Before Any Commit

- [ ] All tests pass (`uv run pytest`)
- [ ] Type checking passes (`uv run ty check`)
- [ ] Linting passes (`uv run ruff check`)
- [ ] Code formatted (`uv run ruff format`)
- [ ] Coverage maintained or improved

### Before PR Merge

- [ ] All user story acceptance criteria met
- [ ] Integration tests demonstrate independent story functionality
- [ ] Documentation updated (docstrings, README if needed)
- [ ] No TODOs or placeholder code
- [ ] Quickstart/demo validated if applicable

## Development Workflow

### Feature Development Process

1. **Specify**: Write user stories with acceptance criteria (spec.md)
2. **Plan**: Research & design, define structure (plan.md, data-model.md, contracts/)
3. **Test**: Write failing tests from acceptance criteria
4. **Approve**: Get user sign-off on failing test behavior
5. **Implement**: Write minimal code to pass tests
6. **Refactor**: Improve design while keeping tests green
7. **Validate**: Run full test suite, check coverage, verify story independently

### Dependency Management Rules

- Add production deps: `uv add <package>`
- Add dev deps: `uv add <package> --dev`
- Sync after clone/pull: `uv sync`
- Always commit `uv.lock` with dependency changes

### Code Review Checklist

Every code change MUST verify:
- Tests written first and failed before implementation
- All quality gates pass
- No unnecessary complexity introduced
- Type hints and docstrings present
- User story acceptance criteria fully met
- Changes align with constitution principles

## Governance

**Amendment Process**: Constitution changes require:
1. Written justification of need
2. Review against existing principles
3. Update to version number (semantic versioning)
4. Propagation to dependent templates (plan, spec, tasks)
5. Update to this governance section's "Last Amended" date

**Versioning Policy**:
- MAJOR: Backward incompatible governance changes (e.g., removing a principle)
- MINOR: New principle added or material expansion of existing
- PATCH: Clarifications, wording improvements, non-semantic refinements

**Compliance Review**:
- Every PR must verify alignment with constitution principles
- Violations require explicit justification in PR description
- Constitution supersedes all other practices
- When in doubt, refer to Principle V (Simplicity)

**Reference**: For runtime development guidance, see `.github/copilot-instructions.md`

**Version**: 1.0.0 | **Ratified**: 2025-10-17 | **Last Amended**: 2025-10-17
