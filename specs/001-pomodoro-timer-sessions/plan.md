# Implementation Plan: Pomodoro Timer Sessions

**Branch**: `001-pomodoro-timer-sessions` | **Date**: October 17, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-pomodoro-timer-sessions/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a CLI-based Pomodoro timer supporting 25-minute work sessions and 5-minute break sessions. The timer provides countdown display (MM:SS format), manual controls (start, pause, resume, cancel), and dual notifications (visual terminal output + audio bell) on completion. No persistence across app restarts; single timer per session. Technical approach uses Python 3.12+ with stdlib only (no external dependencies), asyncio for timer loop, and simple state machine for session management.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: None (stdlib only - `asyncio`, `datetime`, `time`, `sys`)  
**Storage**: N/A (no persistence per FR-017)  
**Testing**: pytest with pytest-asyncio, pytest-xdist (already configured)  
**Target Platform**: CLI (cross-platform: Windows/Linux/macOS)  
**Project Type**: Single project  
**Performance Goals**: Timer accuracy within 1 second (SC-001, SC-002), 1 Hz display refresh (SC-004)  
**Constraints**: <500ms response to user input (SC-007), <2 seconds notification latency (SC-003)  
**Scale/Scope**: Single user, single active timer, 2 session types (work/break)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify alignment with Pomodoro Timer Constitution (`.specify/memory/constitution.md`):

- [x] **Principle I (Test-First)**: Feature has testable acceptance criteria? Tests will be written before implementation?
  - ✅ All 4 user stories have Given-When-Then acceptance scenarios
  - ✅ Tests will be written from acceptance criteria before any implementation
  
- [x] **Principle II (Type Safety & Quality)**: Plan includes type hints, docstrings, and quality gates?
  - ✅ Python 3.12+ with type hints required
  - ✅ Google-style docstrings enforced by ruff
  - ✅ Quality gates: pytest, ty check, ruff check/format
  
- [x] **Principle III (Incremental)**: Feature broken into independent, prioritized user stories (P1, P2, P3)?
  - ✅ P1: Start and Complete Work Session (core MVP)
  - ✅ P2: Take Short Break (completes basic cycle)
  - ✅ P3: Pause/Resume Sessions
  - ✅ P3: Cancel Active Session
  
- [x] **Principle IV (Modern Tooling)**: Uses uv/ruff/ty/pytest? No manual pyproject.toml edits?
  - ✅ uv for dependency management
  - ✅ ruff for linting and formatting
  - ✅ ty for type checking
  - ✅ pytest with pytest-asyncio, pytest-xdist
  
- [x] **Principle V (Simplicity)**: No premature abstractions? Justified if adding frameworks/patterns?
  - ✅ Stdlib only (no external dependencies)
  - ✅ Simple state machine pattern (justified: 4 clear states)
  - ✅ No framework - CLI using argparse/click if needed in future

**Violations** (must be justified in Complexity Tracking section if checked):
- [ ] Adding dependency when stdlib could work
- [ ] Creating abstraction before 3rd repetition
- [ ] Framework introduction without clear need
- [ ] Skipping tests or implementing before test approval

**Status**: ✅ ALL GATES PASSED - No violations

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
src/pomodoro_timer/
├── __init__.py          # Entry point with main() CLI function (already exists)
├── models/
│   ├── __init__.py
│   ├── session.py       # TimerSession entity with state machine
│   ├── types.py         # SessionType, SessionState enums
│   └── exceptions.py    # Custom exceptions (TimerError, InvalidStateTransition, SessionAlreadyActive)
├── timer/
│   ├── __init__.py
│   ├── engine.py        # Core timer loop (asyncio-based)
│   └── notifications.py # Visual + audio notification handlers
└── cli/
    ├── __init__.py
    ├── display.py       # Terminal UI formatting (MM:SS display)
    └── commands.py      # Command handlers (start, pause, resume, cancel)

tests/
├── integration/
│   ├── __init__.py
│   └── test_timer_workflows.py  # Full user story scenarios
└── unit/
    ├── __init__.py
    ├── test_session.py
    ├── test_engine.py
    ├── test_notifications.py
    ├── test_display.py
    └── test_commands.py
```

**Structure Decision**: Single project structure selected. This is a standalone CLI application with no frontend/backend split. The modular organization separates concerns (models, timer engine, CLI interface) while keeping everything in one cohesive package. Tests mirror the source structure with integration tests for user stories and unit tests for components.

## Complexity Tracking

*No violations - section left empty per constitution requirements.*

---

## Planning Phases Complete

### Phase 0: Research ✅

**Output**: [research.md](./research.md)

**Key Decisions**:
- Timer implementation: `asyncio` event loop with `asyncio.sleep()`
- Time tracking: `time.time()` for accuracy
- Display: ANSI escape codes with `\r` for in-place updates
- Notifications: `\a` terminal bell + visual messages
- State management: Python `enum.Enum` with explicit transitions
- CLI: `argparse` for command parsing
- Testing: `pytest-asyncio` + `freezegun` for time mocking

**Dependencies Added**: 
- Dev only: `pytest-asyncio`, `freezegun`
- Production: None (stdlib only)

### Phase 1: Design & Contracts ✅

**Outputs**:
- [data-model.md](./data-model.md) - Entity definitions and state machine
- [contracts/cli-commands.md](./contracts/cli-commands.md) - CLI command specifications
- [quickstart.md](./quickstart.md) - TDD implementation guide
- Agent context updated (`.github/copilot-instructions.md`)

**Data Model**:
- `SessionType` enum (WORK, BREAK)
- `SessionState` enum (IDLE, RUNNING, PAUSED, COMPLETED)
- `TimerSession` class with state machine (8 valid transitions, 11 invalid)

**Contracts Defined**:
- 5 CLI commands: start, pause, resume, cancel, status
- Exit codes: 0 (success), 1 (error), 2 (invalid state), 3 (interrupted)
- Display format: `STATE: MM:SS` with in-place updates
- Notifications: Visual message + terminal bell (`\a`)

**Project Structure**:
```
src/pomodoro_timer/
├── models/ (types, session)
├── timer/ (engine, notifications)
└── cli/ (display, commands)

tests/
├── integration/ (user story workflows)
└── unit/ (component tests)
```

### Phase 2: Tasks ⏭️

**Next Command**: `/speckit.tasks`

This will generate `tasks.md` with:
- Test specifications for each user story
- Implementation tasks in dependency order
- Definition of Done checklist
- Acceptance criteria validation

---

## Post-Design Constitution Check ✅

Re-verified after Phase 1 design completion:

- [x] **Principle I (Test-First)**: quickstart.md mandates tests before implementation
- [x] **Principle II (Type Safety)**: All models use type hints, data-model.md specifies types
- [x] **Principle III (Incremental)**: P1→P2→P3 delivery order defined in quickstart.md
- [x] **Principle IV (Modern Tooling)**: Only pytest-asyncio/freezegun added (dev deps)
- [x] **Principle V (Simplicity)**: Stdlib only confirmed, no frameworks, state machine justified (4 states)

**Status**: ✅ ALL PRINCIPLES MAINTAINED

---

## Summary for Stakeholders

**What's Built**: CLI Pomodoro timer with work/break sessions, pause/resume, manual controls

**How Long**: 
- P1 (Work sessions): ~4 hours (tests + implementation)
- P2 (Breaks): ~1 hour (extend existing)
- P3 (Pause/Resume): ~2 hours (new state transitions)
- P3 (Cancel): ~1 hour (cleanup logic)
- **Total**: ~8 hours development + testing

**Tech Stack**: Python 3.12+ stdlib only (zero runtime dependencies)

**Quality**: TDD with 90%+ coverage, type-checked, fully tested

**Next Step**: Run `/speckit.tasks` to generate detailed implementation tasks

