# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A bitboard-based Othello/Reversi game implementation written in Python. Features CLI and GUI interfaces, AI opponents with multiple difficulty levels, network play, and comprehensive test coverage.

## Development Commands

### Session Setup (Required for each session)
```bash
# Create and activate virtual environment (if not exists)
python3 -m venv venv
source venv/bin/activate

# Install package in development mode
pip install -e .

# Install test dependencies
pip install pytest pytest-cov
```

### Installation and Setup
```bash
# Install in development mode (after venv activation)
pip install -e .

# Install with test dependencies
pip install -e .[test]
```

### Running the Game
```bash
# CLI game (human vs human)
othello

# CLI with AI opponent
othello --ai --ai-level expert

# AI vs AI demo
othello --ai-vs-ai

# GUI version
othello-gui --vs-ai

# Network play (host)
othello --host localhost:8080

# Network play (connect)
othello --connect localhost:8080
```

### Testing
```bash
# Run all tests with coverage (requires venv activation)
source venv/bin/activate && pytest --cov=src --cov-report=xml --cov-report=term-missing

# Run specific test files
source venv/bin/activate && pytest tests/test_board_comprehensive.py -v
source venv/bin/activate && pytest tests/test_game_integration.py -v
source venv/bin/activate && pytest tests/test_bitboard_math.py -v

# Run tests without pytest (if not installed)
python3 -c "import sys; sys.path.append('src'); from othello.board import BitBoard; board = BitBoard.initial(); print('Test: OK')"
```

### Code Quality
```bash
# CI runs these automatically on push/PR (requires venv activation)
source venv/bin/activate && pytest --cov=src --cov-report=xml --cov-report=term-missing
```

## Architecture

### Core Components
- **`src/othello/board.py`**: Bitboard implementation (`BitBoard` class) - core game logic using 64-bit integers for board representation
- **`src/othello/game.py`**: Game state management (`Game` class) - handles turn tracking, move history, and undo/redo
- **`src/othello/ai.py`**: AI implementation with three difficulty levels (easy/hard/expert) and opening book support
- **`src/othello/cli.py`**: Command-line interface with save/load, time limits, and network play
- **`src/othello/gui.py`**: Tkinter-based GUI with move highlighting and status display
- **`src/othello/network.py`**: Socket-based network play utilities
- **`src/othello/scoreboard.py`**: Persistent game statistics storage

### Key Design Principles
- Immutable `BitBoard` objects - operations return new instances
- 64-bit bitboard representation for high-performance move generation
- Direction-based bit shifting for legal move detection and piece flipping
- Minimal external dependencies (standard library only, except for testing)
- Comprehensive test coverage with multiple test categories

### Bitboard Implementation Details
- Uses two 64-bit integers to represent black and white pieces
- Supports configurable board sizes (default 8x8)
- Direction masks prevent edge wrapping during bit operations
- LSB extraction and bit scanning for efficient move enumeration

### AI Implementation
- **Easy**: Random move selection
- **Hard**: Greedy algorithm (maximizes captured pieces)
- **Expert**: Positional evaluation with opening book (`opening_book.json`)

### Testing Structure
- **Basic tests**: `test_board.py`, `test_game.py`, `test_ai.py`
- **Comprehensive tests**: `test_board_comprehensive.py` (complex scenarios)
- **Integration tests**: `test_game_integration.py` (complete game sequences)
- **Mathematical verification**: `test_bitboard_math.py` (bit operation accuracy)
- **Edge cases**: `test_edge_cases.py` (boundary conditions)

## Project Configuration

- **Package management**: `pyproject.toml` with setuptools
- **Entry points**: `othello` (CLI) and `othello-gui` (GUI)
- **Python requirement**: >=3.8
- **CI/CD**: GitHub Actions with pytest and coverage reporting
- **Source structure**: `src/othello/` package layout

## File Locations

### Game Data
- Opening book: `src/othello/opening_book.json`
- Scoreboard: `scoreboard.json` (created at runtime)
- Save files: Created via CLI save command (`s`)

### Documentation
- Architecture: `ARCHITECT.md`
- AI design: `AI_DESIGN.md`
- Test documentation: `tests/README_TESTS.md`
- Main documentation: `README.md`

## Network Play
- Uses socket communication with timeout and retry logic
- Host becomes black player, client becomes white
- Connection status logged through internal logger
- Supports `--host HOST:PORT` and `--connect HOST:PORT` options

## Issue Resolution Workflow

### 📋 Standard Process for GitHub Issues

#### 1. Issue Investigation and Analysis
```bash
# Analyze the issue and create todo list
# Use TodoWrite tool to track progress
```

#### 2. Slack Notifications
```bash
# Start work notification
./scripts/notify_issue_start.sh <issue_number> "Issue Title" <priority>

# Completion notification  
./scripts/notify_issue_complete.sh <issue_number> "Issue Title" "Solution Summary" <commit_hash> "Additional Notes"
```

#### 3. Development and Testing
```bash
# Create feature branch
git checkout -b fix/issue-description

# Implement fixes with comprehensive testing
# Write security tests for security issues
# Ensure all existing tests continue to pass
source venv/bin/activate && pytest --cov=src --cov-report=term-missing
```

#### 4. Commit and PR Creation
```bash
# Commit with detailed message
git commit -m "Fix #XX: Issue description

Detailed explanation of changes:
1. Security improvement 1
2. Feature addition 2
3. Test coverage 3

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push and create PR
git push origin feature-branch
gh pr create --title "Fix #XX: Issue Title" --body "Detailed PR description"
```

#### 5. PR Review Response (MANDATORY AFTER EACH PR)
```bash
# Check for reviews on previously submitted PRs
gh pr list --state open

# For each PR with reviews, analyze feedback and decide:
# 1. Address feedback if needed (implement changes)
# 2. Comment with reasoning if changes not needed
# 3. Create new issues for complex changes requiring separate PRs

# Example: Address review feedback
git checkout pr-branch
# Make necessary changes
git commit -m "Address PR review feedback: specific change"
git push

# Example: Comment on review if no changes needed
gh pr comment <PR_NUMBER> --body "Reasoning why change is not needed"

# Example: Create new issue for complex feedback
gh issue create --title "Issue Title" --body "Description from PR feedback"
```

#### 6. PR Requirements
- **Security Issues**: Must include comprehensive security tests
- **All Issues**: Must maintain backward compatibility
- **All Issues**: Must pass full test suite
- **All Issues**: Must include detailed commit messages
- **All Issues**: Must create individual PRs (one issue per PR)
- **MANDATORY**: Address review feedback before proceeding to next issue

### 🔧 Available Notification Scripts
- `scripts/slack_notify.sh "message"` - Basic notification
- `scripts/notify_issue_start.sh` - Issue start notification
- `scripts/notify_issue_complete.sh` - Issue completion notification

### 📊 Current Issue Priority Queue
1. **🔴 Critical/High Security Issues** (64, 65, 66)
2. **🟡 Medium Performance/Logic Issues** (67, 68, 69)  
3. **🔧 Low Development/Build Issues** (70)

## Development Notes
- Game uses `a1`-`h8` coordinate notation
- Undo (`u`), redo (`r`), save (`s`), load (`l`) commands available in CLI
- GUI shows legal moves highlighting and real-time score display
- All tests can be run individually without pytest if needed
- AI difficulty affects both move selection algorithm and opening book usage