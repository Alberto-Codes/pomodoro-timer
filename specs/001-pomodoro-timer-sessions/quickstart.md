# Quickstart Guide: Pomodoro Timer Sessions

**Created**: October 17, 2025  
**Feature**: Pomodoro Timer Sessions (001)  
**Audience**: Developers implementing this feature

## Overview

This guide provides step-by-step instructions for implementing the Pomodoro Timer Sessions feature following the TDD workflow mandated by Constitution Principle I.

## Prerequisites

- Python 3.12+ installed
- `uv` package manager configured
- Repository cloned and on branch `001-pomodoro-timer-sessions`

## Implementation Workflow

### Phase 1: Environment Setup

```powershell
# Verify Python version
python --version  # Should be 3.12+

# Install development dependencies
uv add pytest-asyncio --dev
uv add freezegun --dev

# Verify tooling works
uv run pytest --version
uv run ty check --version
uv run ruff --version
```

### Phase 2: Write Tests First (P1 - Work Session)

**🚨 CRITICAL**: Tests must be written AND approved by user before any implementation!

#### Step 1: Create Test Structure

```powershell
# Create test directories
New-Item -ItemType Directory -Force -Path tests\unit
New-Item -ItemType Directory -Force -Path tests\integration
New-Item -ItemType File -Path tests\__init__.py
New-Item -ItemType File -Path tests\unit\__init__.py
New-Item -ItemType File -Path tests\integration\__init__.py
```

#### Step 2: Write Unit Tests for Session Model

Create `tests/unit/test_session.py`:

```python
"""Unit tests for TimerSession model."""
import pytest
from pomodoro_timer.models.session import TimerSession
from pomodoro_timer.models.types import SessionType, SessionState


class TestSessionCreation:
    """Test TimerSession initialization."""
    
    def test_new_session_is_idle(self):
        """New session should start in IDLE state."""
        session = TimerSession()
        assert session.state == SessionState.IDLE
    
    def test_new_session_has_no_type(self):
        """New session should have no session type until started."""
        session = TimerSession()
        assert session.session_type is None


class TestStartWorkSession:
    """Test starting work sessions."""
    
    def test_start_work_from_idle(self):
        """Should successfully start work session from IDLE."""
        session = TimerSession()
        session.start_work()
        
        assert session.state == SessionState.RUNNING
        assert session.session_type == SessionType.WORK
        assert session.remaining_seconds == 1500  # 25 minutes
    
    def test_start_work_raises_when_already_running(self):
        """Should raise error when starting work while session active."""
        session = TimerSession()
        session.start_work()
        
        with pytest.raises(Exception):  # Replace with SessionAlreadyActive
            session.start_work()


# Add more tests for pause, resume, cancel, state transitions...
```

#### Step 3: Write Integration Tests for User Stories

Create `tests/integration/test_timer_workflows.py`:

```python
"""Integration tests for complete user workflows (acceptance scenarios)."""
import pytest
import asyncio
from freezegun import freeze_time
from pomodoro_timer.models.session import TimerSession
from pomodoro_timer.timer.engine import TimerEngine


class TestUserStory1WorkSession:
    """Test P1: Start and Complete Work Session."""
    
    @freeze_time("2025-10-17 10:00:00", tick=True)
    @pytest.mark.asyncio
    async def test_acceptance_scenario_1_start_work_countdown(self):
        """Given idle, When start work, Then countdown from 25 minutes."""
        engine = TimerEngine()
        
        # Given: timer is idle
        assert engine.session.state == SessionState.IDLE
        
        # When: user starts work session
        await engine.start_work()
        
        # Then: timer begins counting down from 25 minutes
        assert engine.session.state == SessionState.RUNNING
        assert engine.session.remaining_seconds == 1500
    
    @freeze_time("2025-10-17 10:00:00", tick=True)
    @pytest.mark.asyncio
    async def test_acceptance_scenario_2_work_completion_notification(self):
        """Given running, When timer reaches zero, Then notify completion."""
        engine = TimerEngine()
        
        # Given: work session is running
        await engine.start_work()
        assert engine.session.state == SessionState.RUNNING
        
        # When: timer reaches zero (advance time 25 minutes)
        await asyncio.sleep(1500)  # freezegun will fast-forward
        
        # Then: user is notified that work session is complete
        assert engine.session.state == SessionState.COMPLETED
        assert engine.session.remaining_seconds == 0
        # TODO: Verify notification was sent (mock/spy needed)


# Add tests for all acceptance scenarios from spec.md...
```

#### Step 4: Run Tests (They Should Fail)

```powershell
# Run all tests - expect failures
uv run pytest tests/ -v

# Expected output: all tests should fail (Red phase of TDD)
```

#### Step 5: Get User Approval

**🛑 STOP HERE**

Show failing tests to user/stakeholder and get approval that test behavior matches requirements. This is the contract - implementation will make these pass.

### Phase 3: Implement to Pass Tests (Red → Green)

Only after test approval, begin implementation in this order:

#### Step 1: Implement Data Model

Create `src/pomodoro_timer/models/types.py`:

```python
"""Enums for session types and states."""
import enum


class SessionType(enum.Enum):
    """Types of Pomodoro timer sessions."""
    WORK = "work"
    BREAK = "break"
    
    @property
    def duration_seconds(self) -> int:
        """Get duration in seconds for this session type."""
        return 1500 if self == SessionType.WORK else 300


class SessionState(enum.Enum):
    """States of a timer session lifecycle."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
```

Create `src/pomodoro_timer/models/session.py` following `data-model.md`.

Run tests: `uv run pytest tests/unit/test_session.py -v`

#### Step 2: Implement Timer Engine

Create `src/pomodoro_timer/timer/engine.py` following research patterns.

Run tests: `uv run pytest tests/unit/test_engine.py -v`

#### Step 3: Implement Display

Create `src/pomodoro_timer/cli/display.py`.

Run tests: `uv run pytest tests/unit/test_display.py -v`

#### Step 4: Implement CLI Commands

Create `src/pomodoro_timer/cli/commands.py`.

Update `src/pomodoro_timer/__init__.py` main() function.

Run integration tests: `uv run pytest tests/integration/ -v`

### Phase 4: Refactor (Green → Clean)

Once all tests pass:

1. **Check Code Quality**:
```powershell
uv run ruff check src/ tests/
uv run ruff format src/ tests/
uv run ty check
```

2. **Measure Coverage**:
```powershell
uv run pytest --cov=src --cov-report=term-missing
```

3. **Refactor** if needed:
   - Extract repeated patterns
   - Improve naming
   - Add docstrings
   - Keep tests green!

### Phase 5: Manual Validation

```powershell
# Install the package in editable mode
uv pip install -e .

# Test manually
pomodoro-timer start work
# Let it run for a few seconds
pomodoro-timer pause
pomodoro-timer resume
pomodoro-timer cancel

# Verify behavior matches acceptance criteria
```

## Incremental Delivery

### P1 - Work Session (MVP)

**Goal**: User can start and complete a 25-minute work session.

**Tests to Write**:
- Unit: SessionType enum, SessionState enum, TimerSession.start_work()
- Integration: Full work session workflow with notifications

**Implementation Order**:
1. models/types.py (enums)
2. models/session.py (state machine)
3. timer/engine.py (countdown logic)
4. timer/notifications.py (visual + audio)
5. cli/display.py (MM:SS formatting)
6. cli/commands.py (start command)
7. __init__.py (wire it together)

**Validation**: Run `pomodoro-timer start work` and let it complete. Verify notification.

### P2 - Break Session (Complete Cycle)

**Goal**: User can start a 5-minute break after work.

**Additional Tests**:
- Unit: TimerSession.start_break()
- Integration: Work → Break cycle

**Implementation**: Extend existing command handlers, minimal new code.

**Validation**: Complete full work-break cycle manually.

### P3 - Pause/Resume

**Goal**: User can pause and resume sessions.

**Additional Tests**:
- Unit: TimerSession.pause(), TimerSession.resume()
- Integration: Pause during work, resume, complete

**Implementation**: Add pause/resume methods, update CLI.

**Validation**: Pause during session, verify time preserved on resume.

### P3 - Cancel

**Goal**: User can cancel active sessions.

**Additional Tests**:
- Unit: TimerSession.cancel()
- Integration: Cancel from various states

**Implementation**: Add cancel method, update CLI.

**Validation**: Cancel from running, paused, completed states.

## Quality Gates Checklist

Before committing ANY code:

- [ ] All tests written first
- [ ] User approved test behavior
- [ ] All tests pass (`uv run pytest`)
- [ ] Type checking passes (`uv run ty check`)
- [ ] Linting passes (`uv run ruff check`)
- [ ] Code formatted (`uv run ruff format`)
- [ ] Coverage ≥ 90% (`uv run pytest --cov`)
- [ ] Manual validation complete
- [ ] Docstrings on all public interfaces
- [ ] No TODO comments or placeholder code

## Common Pitfalls

❌ **Don't**:
- Write implementation before tests
- Skip user approval of failing tests
- Commit with failing tests
- Add dependencies without justification
- Create abstractions before 3rd repetition

✅ **Do**:
- Follow Red-Green-Refactor religiously
- Get approval at every test milestone
- Run full quality gates before commit
- Keep implementation simple (stdlib only)
- Document design decisions in comments

## Troubleshooting

### Tests Import Errors

```powershell
# Ensure package is installed in editable mode
uv pip install -e .
```

### Async Tests Failing

```powershell
# Ensure pytest-asyncio is installed
uv add pytest-asyncio --dev

# Mark tests with @pytest.mark.asyncio
```

### Type Checking Errors

```powershell
# Check specific file
uv run ty check src/pomodoro_timer/models/session.py

# Add type hints to fix errors
```

## Next Steps

After P3 complete:

1. Update `README.md` with user-facing usage guide
2. Create `CHANGELOG.md` entry
3. Prepare PR with:
   - All tests passing
   - Quality gates passed
   - Manual validation video/screenshots
   - Link to this feature spec

## References

- [spec.md](../spec.md) - Feature requirements
- [plan.md](../plan.md) - Implementation plan
- [data-model.md](../data-model.md) - Entity definitions
- [contracts/cli-commands.md](../contracts/cli-commands.md) - CLI specification
- [research.md](../research.md) - Technical decisions
- `.specify/memory/constitution.md` - Project principles
