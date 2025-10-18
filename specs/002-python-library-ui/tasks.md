---
description: "Implementation tasks for Python Library-Based UI feature"
---

# Tasks: Python Library-Based UI

**Input**: Design documents from `/specs/002-python-library-ui/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ui-components.md

**Tests**: Per Constitution Principle I (Test-First Development - NON-NEGOTIABLE), ALL features MUST include test tasks. Tests are written FIRST, get user approval while failing, then implementation proceeds. This is mandatory for Pomodoro Timer project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions
- Single project structure: `src/pomodoro_timer/`, `tests/` at repository root
- UI module: `src/pomodoro_timer/ui/`
- UI tests: `tests/ui/` and `tests/integration/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and basic structure

- [ ] T001 Add NiceGUI dependency via `uv add nicegui`
- [ ] T002 Add tomli-w dependency for TOML writing via `uv add tomli-w`
- [ ] T003 Create UI module directory structure: `src/pomodoro_timer/ui/`, `src/pomodoro_timer/ui/components/`, `src/pomodoro_timer/ui/pages/`
- [ ] T004 Create UI test directory structure: `tests/ui/` for acceptance tests
- [ ] T005 Configure pytest for NiceGUI in `pytest.ini` (asyncio_mode=auto, add `pytest_plugins = ["nicegui.testing.user_plugin"]`)
- [ ] T006 Create `tests/ui/__init__.py` and `tests/ui/conftest.py` with test fixtures
- [ ] T007 [P] Create empty `src/pomodoro_timer/ui/__init__.py` with module docstring
- [ ] T008 [P] Create empty `src/pomodoro_timer/ui/components/__init__.py`
- [ ] T009 [P] Create empty `src/pomodoro_timer/ui/pages/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models, state management, and persistence infrastructure that MUST be complete before ANY UI component can be built

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Foundational Models & Infrastructure

- [ ] T010 [P] Create `CompletedSession` dataclass in `src/pomodoro_timer/ui/models.py` with factory methods and computed properties per data-model.md
- [ ] T011 [P] Create `TimerConfig` dataclass in `src/pomodoro_timer/ui/models.py` with validation, default values, and MIN/MAX constants per data-model.md
- [ ] T012 Create `AppState` class in `src/pomodoro_timer/ui/state.py` with session, engine, history, config properties and computed properties per contracts
- [ ] T013 [P] Create `SessionDatabase` class in `src/pomodoro_timer/ui/database.py` with schema initialization, insert, query, and delete methods per contracts
- [ ] T014 [P] Create `ConfigManager` class in `src/pomodoro_timer/ui/config.py` with load, save, and reset methods using tomllib/tomli-w per contracts

### Unit Tests for Foundational Components (REQUIRED) ⚠️

- [ ] T015 [P] Write unit tests for `CompletedSession` in `tests/unit/test_completed_session.py` (factory methods, computed properties, validation)
- [ ] T016 [P] Write unit tests for `TimerConfig` in `tests/unit/test_timer_config.py` (defaults, validation, TOML round-trip not yet implemented)
- [ ] T017 [P] Write unit tests for `AppState` in `tests/unit/test_app_state.py` (computed properties, state delegation, progress calculation)
- [ ] T018 [P] Write integration tests for `SessionDatabase` in `tests/integration/test_session_database.py` (insert, query, indexes, pagination)

**Checkpoint**: Foundation ready - UI component implementation can now begin in parallel

---

## Phase 3: User Story 1 & 2 - Visual Timer Display + Controls (Priority: P1) 🎯 MVP

**Goal**: Users can see a visual timer counting down and interact with it via Start/Pause/Resume/Stop buttons - delivering a complete, functional Pomodoro timer with visual interface

**Why Combined**: These two P1 stories are tightly coupled - a display without controls or controls without display provides no value. Together they form the Minimum Viable Product (MVP).

**Independent Test**: Launch UI, click Start Work, verify timer displays 25:00 and counts down every second, click Pause to pause, click Resume to continue, click Cancel to reset to idle. Timer display and controls should work together seamlessly.

### Acceptance Tests for MVP (REQUIRED - Write FIRST, Verify FAIL, Get USER APPROVAL) ⚠️

- [ ] T019 [P] [US1] Write acceptance test for timer display idle state in `tests/ui/test_timer_display.py` - verify shows "00:00", "Idle", and no progress
- [ ] T020 [P] [US1] Write acceptance test for timer display during work session in `tests/ui/test_timer_display.py` - verify shows "25:00", "Work", "Running" badge, and countdown updates every second
- [ ] T021 [P] [US1] Write acceptance test for session completion display in `tests/ui/test_timer_display.py` - verify timer reaches "00:00" and updates to show completion
- [ ] T022 [P] [US2] Write acceptance test for starting work session in `tests/ui/test_timer_controls.py` - verify clicking "Start Work" button starts timer and changes button states
- [ ] T023 [P] [US2] Write acceptance test for pause/resume in `tests/ui/test_timer_controls.py` - verify clicking Pause stops countdown, Resume continues from same time
- [ ] T024 [P] [US2] Write acceptance test for cancel action in `tests/ui/test_timer_controls.py` - verify clicking Cancel resets to idle state with "00:00"
- [ ] T025 [US1] [US2] Write integration test for complete timer lifecycle in `tests/integration/test_timer_lifecycle.py` - start work → pause → resume → complete, verify all state transitions

**⚠️ STOP**: Verify ALL tests above FAIL appropriately. Get USER APPROVAL that failing tests correctly represent acceptance criteria before proceeding to implementation.

### Implementation for MVP

- [ ] T026 [P] [US1] Implement `timer_display()` component in `src/pomodoro_timer/ui/components/timer_display.py` per contracts (refreshable, shows time/type/progress/state)
- [ ] T027 [P] [US2] Implement `control_buttons()` component in `src/pomodoro_timer/ui/components/controls.py` per contracts (conditional buttons, async handlers, error handling)
- [ ] T028 [US1] [US2] Implement `main_content()` and `main_page()` in `src/pomodoro_timer/ui/pages/main.py` combining timer display and controls with 1-second refresh timer
- [ ] T029 [US1] [US2] Create `run_ui()` function in `src/pomodoro_timer/ui/app.py` to initialize NiceGUI app with main page route and run server on port 8080
- [ ] T030 [US1] [US2] Update `main()` function in `src/pomodoro_timer/__init__.py` to check for `--ui` flag and call `run_ui()` from ui.app module
- [ ] T031 [US1] [US2] Add public API exports to `src/pomodoro_timer/ui/__init__.py` (run_ui, AppState, app_state global)

**Checkpoint**: At this point, the MVP should be fully functional - users can launch the UI, see a visual timer, and control it with buttons. Run ALL acceptance tests to verify.

---

## Phase 4: User Story 3 - Session History View (Priority: P2)

**Goal**: Users can view a list of completed Pomodoro sessions with timestamps and duration information for productivity tracking

**Independent Test**: Complete 3-4 timer sessions (mix of work and break), navigate to history view, verify all completed sessions appear with correct timestamps, durations, and types. Verify sessions are grouped by date. Clear history and verify list empties.

### Tests for User Story 3 (REQUIRED - Write FIRST) ⚠️

- [ ] T032 [P] [US3] Write integration test for session persistence in `tests/integration/test_session_history.py` - complete session, verify saved to database with correct data
- [ ] T033 [P] [US3] Write integration test for history loading in `tests/integration/test_session_history.py` - create multiple sessions, load history, verify correct order and pagination
- [ ] T034 [P] [US3] Write integration test for date grouping in `tests/integration/test_session_history.py` - verify sessions grouped by date correctly
- [ ] T035 [US3] Write acceptance test for history view in `tests/ui/test_session_history.py` - complete sessions, verify history table displays all sessions with correct columns (Type, Date, Time Range, Duration)
- [ ] T036 [US3] Write acceptance test for history updates in `tests/ui/test_session_history.py` - verify history refreshes automatically when new session completes
- [ ] T037 [US3] Write acceptance test for clear history in `tests/ui/test_session_history.py` - verify clear history button shows confirmation and empties history

**⚠️ STOP**: Verify ALL tests above FAIL. Get USER APPROVAL before implementing.

### Implementation for User Story 3

- [ ] T038 [US3] Implement `session_history()` component in `src/pomodoro_timer/ui/components/history.py` per contracts (table with Type/Date/Time/Duration columns, pagination, clear button)
- [ ] T039 [US3] Add `record_completion()` method implementation to `AppState` in `src/pomodoro_timer/ui/state.py` to save completed sessions to database and observable list
- [ ] T040 [US3] Add `load_history()` method implementation to `AppState` in `src/pomodoro_timer/ui/state.py` to load recent sessions from database with pagination
- [ ] T041 [US3] Add `get_history_by_date()` method implementation to `AppState` in `src/pomodoro_timer/ui/state.py` to filter sessions by date
- [ ] T042 [US3] Add `clear_history()` method implementation to `AppState` in `src/pomodoro_timer/ui/state.py` to delete all sessions with confirmation dialog
- [ ] T043 [US3] Integrate `session_history()` component into `main_page()` in `src/pomodoro_timer/ui/pages/main.py` below timer display
- [ ] T044 [US3] Add session completion detection to timer engine integration - call `app_state.record_completion()` when session reaches COMPLETED state

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work - timer display, controls, and history tracking. Run ALL tests to verify independence.

---

## Phase 5: User Story 4 - Session Configuration (Priority: P3)

**Goal**: Users can configure timer durations for work sessions, short breaks, and long breaks through the UI settings, with persistence across app restarts

**Independent Test**: Open settings, change work duration from 25 to 30 minutes, change short break from 5 to 10 minutes, save settings, restart app, start work session, verify timer starts at 30:00 instead of 25:00. Start break session, verify starts at 10:00. Verify settings persist after app restart.

### Tests for User Story 4 (REQUIRED - Write FIRST) ⚠️

- [ ] T045 [P] [US4] Write integration test for config persistence in `tests/integration/test_config_persistence.py` - save config to TOML, restart, load config, verify values match
- [ ] T046 [P] [US4] Write integration test for config validation in `tests/integration/test_config_persistence.py` - attempt to save invalid durations (0, negative, >999), verify rejection with appropriate errors
- [ ] T047 [P] [US4] Write integration test for config application in `tests/integration/test_config_persistence.py` - change config, verify SessionType enum values updated, start session, verify uses new duration
- [ ] T048 [US4] Write acceptance test for settings form in `tests/ui/test_settings.py` - open settings, verify form shows current values for work and short break durations, long break duration displayed (read-only, derived automatically per Pomodoro technique)
- [ ] T049 [US4] Write acceptance test for settings save in `tests/ui/test_settings.py` - modify work and short break durations, click Save, verify success notification, start new session, verify uses new duration
- [ ] T050 [US4] Write acceptance test for settings validation in `tests/ui/test_settings.py` - enter invalid duration (e.g., 0), verify Save button disabled and error message shown
- [ ] T051 [US4] Write acceptance test for settings persistence in `tests/ui/test_settings.py` - change settings, close and reopen app, verify settings retained

**⚠️ STOP**: Verify ALL tests above FAIL. Get USER APPROVAL before implementing.

### Implementation for User Story 4

- [ ] T052 [P] [US4] Implement `ConfigManager.load()` in `src/pomodoro_timer/ui/config.py` using tomllib to read TOML file, create default if missing
- [ ] T053 [P] [US4] Implement `ConfigManager.save()` in `src/pomodoro_timer/ui/config.py` using tomli-w to write TOML file, validate before saving
- [ ] T054 [P] [US4] Implement `ConfigManager.reset_to_defaults()` in `src/pomodoro_timer/ui/config.py` to overwrite config with DEFAULT_CONFIG values
- [ ] T055 [US4] Implement `settings_form()` component in `src/pomodoro_timer/ui/components/settings.py` per contracts (number inputs for durations, theme select, validation, Save/Cancel/Reset buttons)
- [ ] T056 [US4] Add `load_config()` method implementation to `AppState` in `src/pomodoro_timer/ui/state.py` to load config from ConfigManager and apply to SessionType
- [ ] T057 [US4] Add `save_config()` method implementation to `AppState` in `src/pomodoro_timer/ui/state.py` to validate, save via ConfigManager, and apply to SessionType
- [ ] T058 [US4] Add `apply_config()` method implementation to `AppState` in `src/pomodoro_timer/ui/state.py` to update SessionType.WORK and SessionType.BREAK duration_seconds
- [ ] T059 [US4] Add settings dialog/button to `main_page()` in `src/pomodoro_timer/ui/pages/main.py` (open settings in modal or separate page)
- [ ] T060 [US4] Call `app_state.load_config()` in `run_ui()` startup in `src/pomodoro_timer/ui/app.py` to load and apply saved settings on app launch

**Checkpoint**: All user stories (1, 2, 3, 4) should now be independently functional. Users can see timer, control it, view history, and customize durations.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and enhance overall user experience

### Keyboard Shortcuts (FR-015 Requirement)

- [ ] T061 [P] Implement `setup_keyboard_shortcuts()` in `src/pomodoro_timer/ui/keyboard.py` per contracts (Space for start/pause/resume, Escape for cancel, W for work, B for break)
- [ ] T062 Call `setup_keyboard_shortcuts(app_state)` in `run_ui()` in `src/pomodoro_timer/ui/app.py` to register global shortcuts
- [ ] T063 Write acceptance test for keyboard shortcuts in `tests/ui/test_keyboard_shortcuts.py` - verify Space starts timer, Escape cancels, W/B start work/break

### Notifications & UX Enhancements

- [ ] T064 [P] Add session completion notification in timer display component - show toast/notification when session completes using `ui.notify()`
- [ ] T065 [P] Add error handling for session state transitions - catch InvalidStateTransition and SessionAlreadyActive, show user-friendly notifications
- [ ] T066 [P] Add loading state indicators for async operations (start_work, start_break, resume) to provide visual feedback during state changes
- [ ] T074 [P] Add responsive design CSS/layout to timer display and controls ensuring UI remains usable at 800x600 minimum window size without horizontal scrolling

### Documentation & Validation

- [ ] T067 [P] Update README.md with UI mode usage instructions (`pomodoro-timer --ui`), feature overview, and quickstart link
- [ ] T068 [P] Add UI mode documentation to `docs/` folder if exists (screenshots optional, CLI vs UI comparison)
- [ ] T069 Validate quickstart.md instructions - follow step-by-step guide, verify all code examples work, fix any discrepancies
- [ ] T070 Run full test suite (`uv run pytest`) and verify 100% of tests pass
- [ ] T071 Run type checking (`uv run ty check src/pomodoro_timer/ui/`) and fix any type errors
- [ ] T072 Run linting (`uv run ruff check src/pomodoro_timer/ui/`) and fix any issues
- [ ] T073 Run code formatting (`uv run ruff format src/pomodoro_timer/ui/`) to ensure consistent style

### Performance & Quality Validation

- [ ] T075 [P] Write performance test in `tests/integration/test_performance.py` verifying UI startup time <2 seconds (SC-001)
- [ ] T076 [P] Write performance test in `tests/integration/test_performance.py` verifying timer display update latency <500ms (SC-002)
- [ ] T077 [P] Write acceptance test in `tests/ui/test_timer_display.py` verifying all UI controls remain clickable and responsive while timer is running (SC-004)
- [ ] T078 [P] Write performance test in `tests/integration/test_config_persistence.py` verifying config save and apply completes within 1 second (SC-006)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **MVP - US1+US2 (Phase 3)**: Depends on Foundational (Phase 2) completion
- **US3 (Phase 4)**: Depends on Foundational (Phase 2) completion - Can run in parallel with MVP if staffed, but MVP should be validated first
- **US4 (Phase 5)**: Depends on Foundational (Phase 2) completion - Can run in parallel with US3 if staffed
- **Polish (Phase 6)**: Depends on desired user stories being complete - typically after MVP at minimum

### User Story Dependencies

- **US1+US2 (MVP - P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - THIS IS THE MVP
- **US3 (P2)**: Can start after Foundational (Phase 2) - Integrates with MVP but independently testable (can complete sessions manually in tests)
- **US4 (P3)**: Can start after Foundational (Phase 2) - Completely independent, only affects new sessions

### Within Each User Story

1. **Tests FIRST** (Constitution Principle I - NON-NEGOTIABLE):
   - Write ALL tests for the story
   - Run tests, verify they FAIL appropriately
   - Get USER APPROVAL that tests correctly represent acceptance criteria
   - ONLY THEN proceed to implementation

2. **Implementation Order**:
   - Models before services (if new models needed)
   - Services/state methods before UI components
   - UI components before integration into main page
   - Story complete and independently tested before moving to next priority

### Parallel Opportunities

#### Within Setup (Phase 1):
- T007, T008, T009 (empty __init__.py files) can run in parallel

#### Within Foundational (Phase 2):
- T010, T011 (model dataclasses) can run in parallel
- T013, T014 (database and config managers) can run in parallel after models
- T015, T016, T017, T018 (unit/integration tests) can run in parallel

#### Within MVP (Phase 3):
- T019-T024 (all acceptance tests) can run in parallel
- T026, T027 (timer_display and controls components) can run in parallel after tests pass

#### Within US3 (Phase 4):
- T032, T033, T034, T035, T036, T037 (tests) can run in parallel
- T039, T040, T041, T042 (AppState history methods) can be developed in parallel

#### Within US4 (Phase 5):
- T045, T046, T047, T048, T049, T050, T051 (tests) can run in parallel
- T052, T053, T054 (ConfigManager methods) can run in parallel
- T056, T057, T058 (AppState config methods) can run in parallel

#### Within Polish (Phase 6):
- T061, T064, T065, T066 (keyboard shortcuts, notifications, error handling) can run in parallel
- T067, T068, T069 (documentation) can run in parallel
- T070, T071, T072, T073 (quality gates) should run sequentially after implementation complete

#### Across User Stories (if team capacity allows):
- After Foundational complete: MVP (Phase 3), US3 (Phase 4), US4 (Phase 5) can all start in parallel
- Recommended: Complete MVP first for validation, then parallelize US3 and US4

---

## Parallel Example: MVP (US1+US2)

```bash
# Launch all acceptance tests together after foundational complete:
Task T019: "Write acceptance test for timer display idle state"
Task T020: "Write acceptance test for timer display during work session"
Task T021: "Write acceptance test for session completion display"
Task T022: "Write acceptance test for starting work session"
Task T023: "Write acceptance test for pause/resume"
Task T024: "Write acceptance test for cancel action"
Task T025: "Write integration test for complete timer lifecycle"

# After tests pass, launch UI component implementation in parallel:
Task T026: "Implement timer_display() component"
Task T027: "Implement control_buttons() component"
```

---

## Implementation Strategy

### MVP First (Recommended for Single Developer)

1. **Phase 1**: Setup (T001-T009) - ~1 hour
2. **Phase 2**: Foundational (T010-T018) - ~4 hours
   - **CHECKPOINT**: Run unit tests, verify all pass
3. **Phase 3**: MVP - US1+US2 (T019-T031) - ~6 hours
   - Write tests first (T019-T025)
   - Get user approval on failing tests
   - Implement components (T026-T031)
   - **CHECKPOINT**: Run ALL MVP tests, verify 100% pass, launch UI manually and test interactively
4. **DEPLOY/DEMO MVP**: Working visual Pomodoro timer ✨

At this point, you have a complete, shippable product! Users can:
- See a visual countdown timer
- Start work sessions (25 minutes)
- Start break sessions (5 minutes)  
- Pause and resume sessions
- Cancel sessions
- See progress bars and state indicators

### Incremental Delivery (Add Features After MVP)

5. **Phase 4**: US3 - Session History (T032-T044) - ~4 hours
   - **CHECKPOINT**: Complete sessions, verify history works independently
6. **Phase 5**: US4 - Settings (T045-T060) - ~4 hours
   - **CHECKPOINT**: Change settings, restart app, verify persistence
7. **Phase 6**: Polish (T061-T073) - ~3 hours
   - **CHECKPOINT**: Run full test suite, all quality gates pass

Total estimated time: ~22 hours for complete feature

### Parallel Team Strategy (3 Developers)

**Week 1 - Foundation:**
- All: Phase 1 + Phase 2 together (~1 day)

**Week 1-2 - User Stories (Parallel):**
- Developer A: MVP (US1+US2) - Phase 3 (~1.5 days)
- Developer B: US3 (History) - Phase 4 (~1 day)
- Developer C: US4 (Settings) - Phase 5 (~1 day)

**Week 2 - Integration & Polish:**
- All: Phase 6 together, ensure all stories work together (~0.5 day)

Total elapsed time: ~2-3 days with 3 developers

---

## Checkpoints & Validation

### After Setup (Phase 1):
- [ ] Verify `uv sync` runs without errors
- [ ] Verify directory structure created correctly
- [ ] Verify pytest can discover tests (even if none exist yet)

### After Foundational (Phase 2):
- [ ] Run `uv run pytest tests/unit/test_app_state.py -v` - all pass
- [ ] Run `uv run pytest tests/unit/test_completed_session.py -v` - all pass
- [ ] Run `uv run pytest tests/unit/test_timer_config.py -v` - all pass
- [ ] Run `uv run pytest tests/integration/test_session_database.py -v` - all pass
- [ ] Can import `from pomodoro_timer.ui.state import app_state` in Python REPL

### After MVP (Phase 3):
- [ ] Run `uv run pytest tests/ui/ -v` - all MVP acceptance tests pass
- [ ] Run `uv run pomodoro-timer --ui` - browser opens to http://localhost:8080
- [ ] Manual test: Click "Start Work" → timer shows 25:00 and counts down
- [ ] Manual test: Click "Pause" → timer pauses
- [ ] Manual test: Click "Resume" → timer continues from paused time
- [ ] Manual test: Click "Cancel" → timer resets to 00:00
- [ ] Manual test: Let timer reach 00:00 → state changes to completed
- [ ] Run `uv run ty check src/pomodoro_timer/ui/` - no type errors
- [ ] Run `uv run ruff check src/pomodoro_timer/ui/` - no linting errors

### After US3 (Phase 4):
- [ ] Run `uv run pytest tests/integration/test_session_history.py -v` - all pass
- [ ] Run `uv run pytest tests/ui/test_session_history.py -v` - all pass
- [ ] Manual test: Complete 2-3 sessions → history view shows all sessions
- [ ] Manual test: Check session details (Type, Date, Time, Duration) are correct
- [ ] Manual test: Click "Clear History" → confirmation dialog → history empties

### After US4 (Phase 5):
- [ ] Run `uv run pytest tests/integration/test_config_persistence.py -v` - all pass
- [ ] Run `uv run pytest tests/ui/test_settings.py -v` - all pass
- [ ] Manual test: Open settings → change work duration to 30 → save → restart app → start work → verify 30:00
- [ ] Manual test: Try to enter invalid duration (0 or 1000) → verify validation error shown
- [ ] Check `~/.config/pomodoro-timer/config.toml` exists and contains saved settings

### After Polish (Phase 6):
- [ ] Run full test suite: `uv run pytest -v` - 100% pass
- [ ] Run type checking: `uv run ty check` - no errors
- [ ] Run linting: `uv run ruff check` - no errors
- [ ] Run formatting check: `uv run ruff format --check` - no changes needed
- [ ] Manual test: Press Space → timer starts
- [ ] Manual test: Press Escape → timer cancels
- [ ] Manual test: Press W → work session starts
- [ ] Manual test: Press B → break session starts
- [ ] Verify README.md updated with UI usage instructions
- [ ] Follow quickstart.md guide → verify every step works

---

## Notes

- **[P] tasks** = different files, can run in parallel without conflicts
- **[Story] label** = maps task to specific user story for traceability (US1, US2, US3, US4)
- **Tests are mandatory** - Constitution Principle I requires test-first development
- **US1+US2 combined** - Both are P1 and tightly coupled, together they form the MVP
- Each user story should be independently completable and testable
- **ALWAYS verify tests fail before implementing** (red-green-refactor)
- Commit after each task or logical group for clean history
- Stop at any checkpoint to validate story independently
- Use `--ui` flag to differentiate UI mode from CLI mode
- NiceGUI runs on http://localhost:8080 by default

## Success Metrics

At completion of ALL phases:
- ✅ All 78 tasks complete
- ✅ 100% test pass rate (`uv run pytest`)
- ✅ Zero type errors (`uv run ty check`)
- ✅ Zero linting errors (`uv run ruff check`)
- ✅ All acceptance criteria met for US1, US2, US3, US4
- ✅ Users can launch UI with `pomodoro-timer --ui`
- ✅ Timer displays and controls work flawlessly
- ✅ Session history tracks all completed sessions
- ✅ Settings persist across app restarts
- ✅ Keyboard shortcuts functional
- ✅ Documentation updated and validated
- ✅ Ready for production use! 🎉
