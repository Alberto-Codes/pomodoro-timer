# Tasks: Pomodoro Timer Sessions

**Feature**: Pomodoro Timer Sessions (001-pomodoro-timer-sessions)  
**Created**: October 17, 2025  
**Input**: Design documents from `/specs/001-pomodoro-timer-sessions/`

**Tests**: Per Constitution Principle I (Test-First Development - NON-NEGOTIABLE), ALL features MUST include test tasks. Tests are written FIRST, get user approval while failing, then implementation proceeds. This is mandatory for Pomodoro Timer project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Convention
Single project structure (per plan.md):
- Source: `src/pomodoro_timer/`
- Tests: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and test dependencies

- [ ] T001 Install pytest-asyncio development dependency via `uv add pytest-asyncio --dev`
- [ ] T002 Install freezegun development dependency via `uv add freezegun --dev`
- [ ] T003 [P] Create test directory structure: `tests/unit/` and `tests/integration/`
- [ ] T004 [P] Create test __init__.py files in `tests/`, `tests/unit/`, `tests/integration/`
- [ ] T005 [P] Create source directory structure: `src/pomodoro_timer/models/`, `src/pomodoro_timer/timer/`, `src/pomodoro_timer/cli/`
- [ ] T006 [P] Create source __init__.py files in `src/pomodoro_timer/models/`, `src/pomodoro_timer/timer/`, `src/pomodoro_timer/cli/`

**Checkpoint**: Project structure ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core enums and exceptions that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 [P] Create SessionType enum in `src/pomodoro_timer/models/types.py` with WORK and BREAK values, duration_seconds property (1500 for WORK, 300 for BREAK), and display_name property
- [ ] T008 [P] Create SessionState enum in `src/pomodoro_timer/models/types.py` with IDLE, RUNNING, PAUSED, COMPLETED values and display_name property
- [ ] T009 [P] Create custom exceptions in `src/pomodoro_timer/models/exceptions.py`: TimerError (base), InvalidStateTransition, SessionAlreadyActive
- [ ] T010 Write unit tests for SessionType enum in `tests/unit/test_types.py` covering duration_seconds and display_name properties
- [ ] T011 Write unit tests for SessionState enum in `tests/unit/test_types.py` covering display_name property
- [ ] T012 Run tests to verify enums work correctly: `uv run pytest tests/unit/test_types.py -v`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Start and Complete Work Session (Priority: P1) 🎯 MVP

**Goal**: User can start a 25-minute work session and receive notification when it completes

**Independent Test**: Start timer, verify countdown from 25:00, let it complete, verify notification (visual + audio) at 00:00

### Tests for User Story 1 (REQUIRED - Write First, Get Approval) ⚠️

**🚨 CRITICAL**: Write these tests FIRST, ensure they FAIL, get USER APPROVAL on test behavior, THEN implement

- [ ] T013 [P] [US1] Write unit test for TimerSession initialization in `tests/unit/test_session.py`: new session should be in IDLE state with no session type
- [ ] T014 [P] [US1] Write unit test for TimerSession.start_work() in `tests/unit/test_session.py`: should transition from IDLE to RUNNING with WORK type and 1500 seconds
- [ ] T015 [P] [US1] Write unit test for TimerSession.start_work() error case in `tests/unit/test_session.py`: should raise SessionAlreadyActive when called while session is already running
- [ ] T016 [P] [US1] Write unit test for TimerSession.tick() in `tests/unit/test_session.py`: should decrease remaining_seconds and transition to COMPLETED when reaching zero
- [ ] T017 [P] [US1] Write unit test for TimerSession state machine in `tests/unit/test_session.py`: verify IDLE → RUNNING → COMPLETED transitions
- [ ] T018 [P] [US1] Write integration test for acceptance scenario 1 in `tests/integration/test_timer_workflows.py`: Given idle, When start work, Then countdown from 25 minutes (use @freeze_time and @pytest.mark.asyncio)
- [ ] T019 [P] [US1] Write integration test for acceptance scenario 2 in `tests/integration/test_timer_workflows.py`: Given running, When timer reaches zero, Then notify completion (mock time with freezegun)
- [ ] T020 [P] [US1] Write integration test for acceptance scenario 3 in `tests/integration/test_timer_workflows.py`: Given running, When check timer, Then display remaining time accurately
- [ ] T021 [US1] Run all User Story 1 tests and verify they FAIL: `uv run pytest tests/ -v -k "US1 or session or workflow"`
- [ ] T022 [US1] **🛑 STOP**: Present failing tests to user/stakeholder for approval of test behavior before ANY implementation

### Implementation for User Story 1 (Only After Test Approval)

- [ ] T023 [P] [US1] Create TimerSession class in `src/pomodoro_timer/models/session.py` with __init__, state, session_type, remaining_seconds, start_time, end_time attributes (all with type hints)
- [ ] T024 [P] [US1] Add TimerSession.start_work() method in `src/pomodoro_timer/models/session.py` with state validation and transition logic
- [ ] T025 [P] [US1] Add TimerSession.tick() method in `src/pomodoro_timer/models/session.py` to update remaining time and auto-transition to COMPLETED
- [ ] T026 [P] [US1] Add TimerSession.formatted_time property in `src/pomodoro_timer/models/session.py` returning MM:SS format
- [ ] T027 [P] [US1] Add TimerSession.is_active property in `src/pomodoro_timer/models/session.py` checking if RUNNING or PAUSED
- [ ] T028 [US1] Run unit tests for session model: `uv run pytest tests/unit/test_session.py -v`
- [ ] T029 [P] [US1] Create TimerEngine class in `src/pomodoro_timer/timer/engine.py` with async countdown loop using asyncio.sleep(0.1) and time.time() for accuracy
- [ ] T030 [P] [US1] Implement TimerEngine.start_work() async method in `src/pomodoro_timer/timer/engine.py` that starts session and runs countdown loop
- [ ] T031 [P] [US1] Write unit tests for TimerEngine in `tests/unit/test_engine.py` covering start_work and countdown loop with mocked time
- [ ] T032 [US1] Run engine tests: `uv run pytest tests/unit/test_engine.py -v`
- [ ] T033 [P] [US1] Create display_timer() function in `src/pomodoro_timer/cli/display.py` using sys.stdout.write('\r...') for in-place MM:SS updates
- [ ] T034 [P] [US1] Create format_time() utility in `src/pomodoro_timer/cli/display.py` to convert seconds to MM:SS string with zero-padding
- [ ] T035 [P] [US1] Write unit tests for display functions in `tests/unit/test_display.py` covering format_time() with various inputs
- [ ] T036 [US1] Run display tests: `uv run pytest tests/unit/test_display.py -v`
- [ ] T037 [P] [US1] Create notify_completion() function in `src/pomodoro_timer/timer/notifications.py` that prints visual message and outputs '\a' for terminal bell
- [ ] T038 [P] [US1] Write unit tests for notifications in `tests/unit/test_notifications.py` using mocked stdout/stderr
- [ ] T039 [US1] Run notification tests: `uv run pytest tests/unit/test_notifications.py -v`
- [ ] T040 [P] [US1] Create start command handler in `src/pomodoro_timer/cli/commands.py` using argparse for 'start work' command
- [ ] T041 [P] [US1] Integrate TimerEngine, display, and notifications in start command handler in `src/pomodoro_timer/cli/commands.py`
- [ ] T042 [US1] Update main() function in `src/pomodoro_timer/__init__.py` to wire argparse and command handlers
- [ ] T043 [US1] Write unit tests for CLI commands in `tests/unit/test_commands.py` covering start command argument parsing and error handling
- [ ] T044 [US1] Run all User Story 1 tests: `uv run pytest tests/ -v -k "US1 or session or engine or display or notification or command or workflow"`
- [ ] T045 [US1] Fix any failing tests until all pass
- [ ] T046 [US1] Run type checking: `uv run ty check`
- [ ] T047 [US1] Run linting: `uv run ruff check src/ tests/`
- [ ] T048 [US1] Run formatting: `uv run ruff format src/ tests/`
- [ ] T049 [US1] Measure code coverage: `uv run pytest --cov=src --cov-report=term-missing`
- [ ] T050 [US1] Manual validation: Install package (`uv pip install -e .`), run `pomodoro-timer start work`, verify countdown, wait for completion, verify notification
- [ ] T051 [US1] Add Google-style docstrings to all public functions/methods/classes in User Story 1 code

**Checkpoint**: User Story 1 (MVP) complete - user can start and complete 25-minute work session with notification

---

## Phase 4: User Story 2 - Take Short Break (Priority: P2)

**Goal**: User can start a 5-minute break session after work session completes

**Independent Test**: Start break timer, verify countdown from 05:00, let it complete, verify break completion notification

### Tests for User Story 2 (REQUIRED - Write First, Get Approval) ⚠️

- [ ] T052 [P] [US2] Write unit test for TimerSession.start_break() in `tests/unit/test_session.py`: should transition from IDLE or COMPLETED to RUNNING with BREAK type and 300 seconds
- [ ] T053 [P] [US2] Write integration test for acceptance scenario 1 in `tests/integration/test_timer_workflows.py`: Given work completed, When start break, Then countdown from 5 minutes
- [ ] T054 [P] [US2] Write integration test for acceptance scenario 2 in `tests/integration/test_timer_workflows.py`: Given break running, When timer reaches zero, Then notify break completion
- [ ] T055 [P] [US2] Write integration test for acceptance scenario 3 in `tests/integration/test_timer_workflows.py`: Given break completed, When ready, Then can start new work session
- [ ] T056 [P] [US2] Write integration test for full work-break cycle in `tests/integration/test_timer_workflows.py`: work session → complete → start break → complete → start work
- [ ] T057 [US2] Run all User Story 2 tests and verify they FAIL: `uv run pytest tests/ -v -k "US2 or break"`
- [ ] T058 [US2] **🛑 STOP**: Get user approval on test behavior

### Implementation for User Story 2

- [ ] T059 [P] [US2] Add TimerSession.start_break() method in `src/pomodoro_timer/models/session.py` similar to start_work() but with BREAK type
- [ ] T060 [P] [US2] Add TimerEngine.start_break() async method in `src/pomodoro_timer/timer/engine.py`
- [ ] T061 [P] [US2] Update notify_completion() in `src/pomodoro_timer/timer/notifications.py` to distinguish between work and break completion messages (FR-015)
- [ ] T062 [P] [US2] Add 'start break' command handler in `src/pomodoro_timer/cli/commands.py`
- [ ] T063 [US2] Update argparse in main() to accept 'break' as session type in `src/pomodoro_timer/__init__.py`
- [ ] T064 [US2] Write unit tests for start_break in `tests/unit/test_session.py`
- [ ] T065 [US2] Write unit tests for break command in `tests/unit/test_commands.py`
- [ ] T066 [US2] Run all User Story 2 tests: `uv run pytest tests/ -v -k "US2 or break"`
- [ ] T067 [US2] Fix any failing tests until all pass
- [ ] T068 [US2] Run quality gates: `uv run ty check && uv run ruff check && uv run ruff format`
- [ ] T069 [US2] Manual validation: Run `pomodoro-timer start work`, let complete, then `pomodoro-timer start break`, verify 5-minute countdown and break notification
- [ ] T070 [US2] Add docstrings to new User Story 2 functions

**Checkpoint**: User Stories 1 AND 2 complete - full work-break cycle functional

---

## Phase 5: User Story 3 - Pause and Resume Sessions (Priority: P3)

**Goal**: User can pause active timer and resume from where it left off

**Independent Test**: Start timer, let run few seconds, pause, verify time preserved, resume, verify countdown continues

### Tests for User Story 3 (REQUIRED - Write First, Get Approval) ⚠️

- [ ] T071 [P] [US3] Write unit test for TimerSession.pause() in `tests/unit/test_session.py`: should transition from RUNNING to PAUSED preserving remaining_seconds
- [ ] T072 [P] [US3] Write unit test for TimerSession.resume() in `tests/unit/test_session.py`: should transition from PAUSED to RUNNING and recalculate end_time
- [ ] T073 [P] [US3] Write unit test for invalid pause in `tests/unit/test_session.py`: should raise InvalidStateTransition when pausing non-RUNNING session
- [ ] T074 [P] [US3] Write unit test for invalid resume in `tests/unit/test_session.py`: should raise InvalidStateTransition when resuming non-PAUSED session
- [ ] T075 [P] [US3] Write integration test for acceptance scenario 1 in `tests/integration/test_timer_workflows.py`: Given running, When pause, Then countdown stops and preserves remaining time
- [ ] T076 [P] [US3] Write integration test for acceptance scenario 2 in `tests/integration/test_timer_workflows.py`: Given paused, When resume, Then countdown continues from where stopped
- [ ] T077 [P] [US3] Write integration test for acceptance scenario 3 in `tests/integration/test_timer_workflows.py`: Given paused, When check display, Then shows paused time and PAUSED state
- [ ] T078 [US3] Run all User Story 3 tests and verify they FAIL: `uv run pytest tests/ -v -k "US3 or pause or resume"`
- [ ] T079 [US3] **🛑 STOP**: Get user approval on test behavior

### Implementation for User Story 3

- [ ] T080 [P] [US3] Add TimerSession.pause() method in `src/pomodoro_timer/models/session.py` with state validation
- [ ] T081 [P] [US3] Add TimerSession.resume() method in `src/pomodoro_timer/models/session.py` with state validation and end_time recalculation
- [ ] T082 [P] [US3] Add TimerEngine.pause() method in `src/pomodoro_timer/timer/engine.py` that stops countdown loop
- [ ] T083 [P] [US3] Add TimerEngine.resume() method in `src/pomodoro_timer/timer/engine.py` that restarts countdown loop
- [ ] T084 [P] [US3] Update display_timer() in `src/pomodoro_timer/cli/display.py` to show "(PAUSED)" indicator when state is PAUSED
- [ ] T085 [P] [US3] Add 'pause' command handler in `src/pomodoro_timer/cli/commands.py`
- [ ] T086 [P] [US3] Add 'resume' command handler in `src/pomodoro_timer/cli/commands.py`
- [ ] T087 [US3] Update argparse in main() to accept 'pause' and 'resume' commands in `src/pomodoro_timer/__init__.py`
- [ ] T088 [US3] Write unit tests for pause/resume in `tests/unit/test_session.py`
- [ ] T089 [US3] Write unit tests for pause/resume commands in `tests/unit/test_commands.py`
- [ ] T090 [US3] Run all User Story 3 tests: `uv run pytest tests/ -v -k "US3 or pause or resume"`
- [ ] T091 [US3] Fix any failing tests until all pass
- [ ] T092 [US3] Run quality gates: `uv run ty check && uv run ruff check && uv run ruff format`
- [ ] T093 [US3] Manual validation: Run `pomodoro-timer start work`, after 10 seconds run `pomodoro-timer pause`, verify time preserved, run `pomodoro-timer resume`, verify countdown continues
- [ ] T094 [US3] Add docstrings to new User Story 3 functions

**Checkpoint**: User Stories 1, 2, AND 3 complete - pause/resume functionality working

---

## Phase 6: User Story 4 - Cancel Active Session (Priority: P3)

**Goal**: User can cancel any active or paused session and return to idle state

**Independent Test**: Start timer, cancel, verify returns to IDLE; start and pause, cancel, verify returns to IDLE

### Tests for User Story 4 (REQUIRED - Write First, Get Approval) ⚠️

- [ ] T095 [P] [US4] Write unit test for TimerSession.cancel() in `tests/unit/test_session.py`: should transition from RUNNING/PAUSED/COMPLETED to IDLE
- [ ] T096 [P] [US4] Write integration test for acceptance scenario 1 in `tests/integration/test_timer_workflows.py`: Given running or paused, When cancel, Then stop and return to IDLE
- [ ] T097 [P] [US4] Write integration test for acceptance scenario 2 in `tests/integration/test_timer_workflows.py`: Given canceled, When start new session, Then begins fresh from full duration
- [ ] T098 [US4] Run all User Story 4 tests and verify they FAIL: `uv run pytest tests/ -v -k "US4 or cancel"`
- [ ] T099 [US4] **🛑 STOP**: Get user approval on test behavior

### Implementation for User Story 4

- [ ] T100 [P] [US4] Add TimerSession.cancel() method in `src/pomodoro_timer/models/session.py` that resets to IDLE state
- [ ] T101 [P] [US4] Add TimerEngine.cancel() method in `src/pomodoro_timer/timer/engine.py` that stops countdown loop and resets session
- [ ] T102 [P] [US4] Add 'cancel' command handler in `src/pomodoro_timer/cli/commands.py`
- [ ] T103 [US4] Update argparse in main() to accept 'cancel' command in `src/pomodoro_timer/__init__.py`
- [ ] T104 [US4] Write unit tests for cancel in `tests/unit/test_session.py`
- [ ] T105 [US4] Write unit tests for cancel command in `tests/unit/test_commands.py`
- [ ] T106 [US4] Run all User Story 4 tests: `uv run pytest tests/ -v -k "US4 or cancel"`
- [ ] T107 [US4] Fix any failing tests until all pass
- [ ] T108 [US4] Run quality gates: `uv run ty check && uv run ruff check && uv run ruff format`
- [ ] T109 [US4] Manual validation: Run `pomodoro-timer start work`, run `pomodoro-timer cancel`, verify returns to idle and can start fresh
- [ ] T110 [US4] Add docstrings to new User Story 4 functions

**Checkpoint**: All 4 user stories complete - full feature functionality delivered

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final quality checks

- [ ] T111 [P] Add 'status' command in `src/pomodoro_timer/cli/commands.py` per contracts/cli-commands.md showing current state without interactive display
- [ ] T112 [P] Write unit tests for status command in `tests/unit/test_commands.py`
- [ ] T113 [P] Add exit code handling in `src/pomodoro_timer/__init__.py`: 0 (success), 1 (error), 2 (invalid state), 3 (interrupted)
- [ ] T114 [P] Handle KeyboardInterrupt (Ctrl+C) gracefully in timer loop in `src/pomodoro_timer/timer/engine.py` with exit code 3
- [ ] T115 [P] Add comprehensive error messages for all InvalidStateTransition cases in `src/pomodoro_timer/models/session.py`
- [ ] T116 [P] Add edge case tests in `tests/unit/test_session.py` for all invalid state transitions from data-model.md
- [ ] T117 [P] Add edge case tests in `tests/integration/test_timer_workflows.py` for edge cases from spec.md (completed state persistence, concurrent session prevention, etc.)
- [ ] T118 Run full test suite with coverage: `uv run pytest --cov=src --cov-report=term-missing --cov-report=html`
- [ ] T119 Verify coverage is ≥90% for all modules
- [ ] T120 Run type checking on entire codebase: `uv run ty check`
- [ ] T121 Run linting on entire codebase: `uv run ruff check src/ tests/`
- [ ] T122 Run formatting on entire codebase: `uv run ruff format src/ tests/`
- [ ] T123 Verify all functions have Google-style docstrings: `uv run ruff check --select D`
- [ ] T124 Run parallel tests to verify no race conditions: `uv run pytest -n auto`
- [ ] T125 [P] Update README.md with usage instructions and examples per quickstart.md patterns
- [ ] T126 [P] Create CHANGELOG.md entry documenting all 4 user stories delivered
- [ ] T127 Manual end-to-end validation following quickstart.md validation steps for all user stories
- [ ] T128 Performance test: Verify timer accuracy over full 25-minute session (use fast-forwarded time in test)
- [ ] T129 Performance test: Verify all commands respond within 500ms (SC-007)
- [ ] T130 Performance test: Verify notifications appear within 2 seconds of completion (SC-003)
- [ ] T131 Final constitution compliance check: Verify all 5 principles maintained
- [ ] T132 Create demo video or screenshots showing all 4 user stories in action

**Checkpoint**: Feature complete, tested, documented, and ready for PR

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001-T006) - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (T007-T012) - Can start once foundation ready
- **User Story 2 (Phase 4)**: Depends on Foundational (T007-T012) - Can start in parallel with US1 if staffed
- **User Story 3 (Phase 5)**: Depends on Foundational (T007-T012) - Can start in parallel with US1/US2 if staffed
- **User Story 4 (Phase 6)**: Depends on Foundational (T007-T012) - Can start in parallel with US1/US2/US3 if staffed
- **Polish (Phase 7)**: Depends on desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Independent - only needs Foundation (T007-T012)
- **US2 (P2)**: Independent - only needs Foundation, extends US1 but testable independently
- **US3 (P3)**: Independent - only needs Foundation, works with US1/US2 but testable independently
- **US4 (P3)**: Independent - only needs Foundation, works with US1/US2/US3 but testable independently

### Within Each User Story

1. Write ALL tests first (REQUIRED per Constitution)
2. Run tests, verify they FAIL
3. Get user approval on test behavior (🛑 MANDATORY STOP)
4. Implement models
5. Implement services/engine
6. Implement UI/CLI
7. Run tests until all pass
8. Quality gates (type check, lint, format)
9. Manual validation
10. Add docstrings

### Parallel Opportunities

- **Setup (Phase 1)**: T003, T004, T005, T006 can all run in parallel
- **Foundational (Phase 2)**: T007, T008, T009 can run in parallel; then T010, T011 parallel
- **User Stories**: After Foundation complete, ALL 4 user stories can be worked on in parallel by different team members
- **Within US1 Tests**: T013-T020 can all be written in parallel
- **Within US1 Implementation**: T023-T027 (session model), T033-T035 (display), T037-T038 (notifications) can run in parallel
- **Within US2 Tests**: T052-T056 can all be written in parallel
- **Within US2 Implementation**: T059, T060, T061, T062 can run in parallel
- **Within US3 Tests**: T071-T077 can all be written in parallel
- **Within US3 Implementation**: T080-T086 can run in parallel
- **Within US4 Tests**: T095-T097 can all be written in parallel
- **Within US4 Implementation**: T100-T102 can run in parallel
- **Polish**: T111-T112, T113-T117, T125-T126 can run in parallel

---

## Parallel Example: User Story 1 Tests

**Before ANY implementation**, write all these tests in parallel:

```bash
# All can be written simultaneously by different developers or AI agents:
T013: Unit test - TimerSession initialization
T014: Unit test - TimerSession.start_work() success
T015: Unit test - TimerSession.start_work() error
T016: Unit test - TimerSession.tick()
T017: Unit test - State machine transitions
T018: Integration - Acceptance scenario 1
T019: Integration - Acceptance scenario 2
T020: Integration - Acceptance scenario 3
```

Then run all tests together (T021) and ensure they fail before ANY implementation.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

**Recommended for solo developer or small team:**

1. Complete T001-T006 (Setup)
2. Complete T007-T012 (Foundational) - CRITICAL BLOCKER
3. Complete T013-T051 (User Story 1) - Full TDD cycle
4. **STOP and VALIDATE**: Test US1 independently, demo to stakeholders
5. Deploy MVP if ready

**Estimated Time**: ~4 hours (per plan.md)

### Incremental Delivery (Priority Order)

**Best for continuous value delivery:**

1. Setup + Foundational (T001-T012) → Foundation ready
2. User Story 1 (T013-T051) → Test independently → Deploy/Demo MVP! 🎯
3. User Story 2 (T052-T070) → Test independently → Deploy/Demo v1.1
4. User Story 3 (T071-T094) → Test independently → Deploy/Demo v1.2
5. User Story 4 (T095-T110) → Test independently → Deploy/Demo v1.3
6. Polish (T111-T132) → Final quality → Deploy/Demo v2.0

**Estimated Total Time**: ~8 hours (per plan.md)

### Parallel Team Strategy

**For team with 4+ developers:**

1. **Together**: Complete Setup + Foundational (T001-T012)
2. **Parallel (Once T012 complete)**:
   - Developer A: User Story 1 (T013-T051)
   - Developer B: User Story 2 (T052-T070)
   - Developer C: User Story 3 (T071-T094)
   - Developer D: User Story 4 (T095-T110)
3. **Together**: Integrate and Polish (T111-T132)

**Estimated Time**: ~2-3 hours (if parallelized)

---

## Quality Gates Checklist

Before marking ANY user story complete:

- [ ] All tests for that story written FIRST and got user approval
- [ ] All tests for that story pass: `uv run pytest -k "US#"`
- [ ] Type checking passes: `uv run ty check`
- [ ] Linting passes: `uv run ruff check`
- [ ] Code formatted: `uv run ruff format`
- [ ] Coverage ≥90% for story modules
- [ ] All public functions have Google-style docstrings
- [ ] Manual validation successful
- [ ] Story independently testable (can demo without other stories)
- [ ] No TODO comments or placeholder code

---

## Success Metrics (from spec.md Success Criteria)

Validate these during Phase 7:

- [ ] **SC-001**: 25-minute work session accurate within 1 second
- [ ] **SC-002**: 5-minute break session accurate within 1 second
- [ ] **SC-003**: Notifications appear within 2 seconds of timer reaching zero
- [ ] **SC-004**: Display refreshes at least 1 Hz (once per second)
- [ ] **SC-005**: 95% of users complete first work-break cycle without errors (test with manual validation)
- [ ] **SC-006**: Pause/resume preserves time within 1 second accuracy
- [ ] **SC-007**: All commands respond within 500 milliseconds

---

## Task Summary

**Total Tasks**: 132
- **Setup**: 6 tasks (T001-T006)
- **Foundational**: 6 tasks (T007-T012)
- **User Story 1 (P1)**: 39 tasks (T013-T051) - MVP
- **User Story 2 (P2)**: 19 tasks (T052-T070)
- **User Story 3 (P3)**: 24 tasks (T071-T094)
- **User Story 4 (P3)**: 16 tasks (T095-T110)
- **Polish**: 22 tasks (T111-T132)

**Parallel Opportunities**: 58 tasks marked [P] can run in parallel within their phase

**Independent Stories**: All 4 user stories are independently implementable and testable

**Suggested MVP**: User Story 1 only (39 tasks + Setup + Foundational = 51 tasks) - delivers core value

---

## Notes

- **[P] marker**: Different files, no dependencies, safe to parallelize
- **[Story] marker**: Maps task to specific user story for traceability
- **TDD Workflow**: Tests → Fail → Approval → Implement → Pass → Refactor
- **Constitution Compliance**: All 5 principles maintained throughout
- **File Paths**: All tasks include exact file paths for clarity
- **Stop Points**: 🛑 markers indicate mandatory user approval before proceeding
- **Checkpoints**: Validate story independence at each checkpoint
- **Quality**: Zero shortcuts - 90%+ coverage, full type hints, complete docstrings
