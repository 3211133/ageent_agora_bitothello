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

### 🚀 Automated Workflow (Recommended)

#### Quick Start Commands
```bash
# Start working on an issue (complete automation)
./scripts/start_issue.sh <issue_number> "Issue Title" <PRIORITY> [analysis_type]

# Complete an issue (complete automation)  
./scripts/complete_issue.sh <issue_number> ["Optional commit summary"] [skip_tests]
```

#### Examples
```bash
# Start security issue
./scripts/start_issue.sh 69 "Test Coverage Issues" "MEDIUM" "security"

# Start AI-related issue
./scripts/start_issue.sh 70 "AI Improvements" "LOW" "ai"

# Complete issue with custom message
./scripts/complete_issue.sh 69 "Enhanced test coverage for critical paths"

# Complete documentation-only issue (skip tests)
./scripts/complete_issue.sh 70 "Updated documentation" true
```

### 🔧 Manual Workflow (Alternative)

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

### 🔧 Available Scripts

#### 🚀 Complete Workflow Automation
- `./scripts/start_issue.sh` - Issue start automation (environment, branch, analysis, notifications)
- `./scripts/complete_issue.sh` - Issue completion automation (testing, commit, PR, notifications)

#### 🛠️ Development Process Automation  
- `./scripts/investigate.sh` - Code investigation and analysis automation
- `./scripts/dev-helper.sh` - Development workflow helpers (testing, quality, watch mode)
- `./scripts/check-reviews.sh` - PR review management and response automation
- `./scripts/quality-check.sh` - Comprehensive quality and security checks
- `./scripts/gemini-review.sh` - AI-powered code review using Google Gemini
- `./scripts/setup-gemini.sh` - Gemini API configuration helper

#### 📢 Individual Notification Scripts
- `scripts/slack_notify.sh "message"` - Basic notification
- `scripts/notify_issue_start.sh` - Issue start notification  
- `scripts/notify_issue_complete.sh` - Issue completion notification

#### Script Features

**🚀 Core Workflow Scripts:**

**start_issue.sh automates:**
1. Environment setup and validation
2. Virtual environment activation
3. Dependency installation check
4. Git branch creation and checkout
5. Baseline testing
6. Issue-specific analysis
7. Slack notifications
8. Summary and next steps

**complete_issue.sh automates:**
1. Environment validation
2. Git status checks
3. Comprehensive testing
4. Issue detail retrieval
5. **Optional Gemini AI pre-PR review** (comprehensive, security, or performance focus)
6. Git operations (commit, push)
7. PR creation with detailed descriptions
8. Slack notifications
9. Cleanup options and next steps

**🔍 Development Process Scripts:**

**investigate.sh provides:**
- Smart code search (function, class, variable, security patterns)
- Git history analysis for related changes
- Dependency mapping and impact assessment
- File modification tracking
- Code metrics and complexity analysis

**dev-helper.sh provides:**
- Quick testing with multiple scopes (changed files, fast, unit, integration, security)
- Watch mode for continuous testing during development
- Code quality checks and syntax validation
- Smart commit helper with pre-commit validation
- Development progress monitoring

**check-reviews.sh provides:**
- Open PR listing with review status
- Detailed review analysis and comment parsing
- Response template generation (addressed, disagree, partial)
- Interactive response helpers
- CI status monitoring for all PRs

**quality-check.sh provides:**
- Security vulnerability scanning (secrets, injections, path traversal)
- Performance analysis and benchmarking
- Code quality metrics (complexity, file sizes, TODOs)
- Test coverage analysis and reporting
- Dependency security auditing

**gemini-review.sh provides:**
- AI-powered comprehensive code review using Google Gemini
- Specialized focus areas (security, performance, maintainability, general)
- Interactive review workflow with actionable feedback
- Review result archiving and documentation
- Integration with complete_issue.sh workflow

### 📊 Current Issue Priority Queue
1. **🔴 Critical/High Security Issues** (64, 65, 66)
2. **🟡 Medium Performance/Logic Issues** (67, 68, 69)  
3. **🔧 Low Development/Build Issues** (70)

## Quick Reference

### Essential Commands
```bash
# 🚀 Core Workflow
./scripts/start_issue.sh <issue_number> "Issue Title" <PRIORITY> [analysis_type]
./scripts/complete_issue.sh <issue_number> ["commit_summary"] [skip_tests]

# 🔍 Development Process
./scripts/investigate.sh <search_type> <search_term> [scope]
./scripts/dev-helper.sh <action> [options]
./scripts/check-reviews.sh [action] [pr_number]
./scripts/quality-check.sh [check_type]
./scripts/gemini-review.sh [scope] [focus_area]

# 📊 Manual Commands (if needed)
source venv/bin/activate && pytest --cov=src --cov-report=term-missing
gh pr list --state open
git status
```

### Common Development Patterns
```bash
# 🎯 Starting work on a security issue
./scripts/start_issue.sh 69 "Fix Security Vulnerability" "HIGH" "security"

# 🔄 Development cycle
./scripts/dev-helper.sh watch fast        # Continuous testing
./scripts/dev-helper.sh test changed      # Test only changed files
./scripts/dev-helper.sh quality           # Check code quality

# 📋 Investigation and analysis
./scripts/investigate.sh function "choose_move" src
./scripts/investigate.sh security "password|token" all

# 👁️ PR review management
./scripts/check-reviews.sh list           # List all PRs
./scripts/check-reviews.sh check 75       # Check specific PR
./scripts/check-reviews.sh respond 75     # Interactive response

# 🛡️ Quality assurance
./scripts/quality-check.sh security       # Security scan
./scripts/quality-check.sh all            # Full quality check

# 🤖 AI-powered code review
./scripts/setup-gemini.sh                 # One-time setup
./scripts/gemini-review.sh staged security # Security-focused AI review
./scripts/gemini-review.sh all general    # Comprehensive AI review

# 🏁 Completing work (includes optional Gemini review)
./scripts/complete_issue.sh 69 "Fixed critical security vulnerability"
```

### Priority Levels
- **CRITICAL**: Security vulnerabilities, crashes
- **HIGH**: Major functionality issues
- **MEDIUM**: Feature improvements, compatibility  
- **LOW**: Development experience, documentation

### Analysis Types (for start_issue.sh)
- `security` - Security-focused analysis
- `memory` - Memory and performance analysis
- `ai` - AI module analysis
- `compatibility` - Compatibility analysis
- (default) - General analysis

### Gemini AI Code Review Setup

#### One-time Setup
```bash
# Run the setup helper
./scripts/setup-gemini.sh

# Manually set API key (alternative)
export GEMINI_API_KEY="your-api-key-here"
# OR create ~/.gemini_api_key file
# OR add to .env file: GEMINI_API_KEY=your-key
```

#### Get API Key
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create API key
4. Run setup script: `./scripts/setup-gemini.sh`

#### Review Focus Areas
- **general**: Comprehensive review (correctness, security, performance, maintainability)
- **security**: Security-focused (vulnerabilities, input validation, auth, crypto)
- **performance**: Performance-focused (complexity, memory, optimization opportunities)
- **maintainability**: Code quality (readability, documentation, testing, refactoring)

#### Usage Examples
```bash
# Standalone reviews
./scripts/gemini-review.sh staged general          # Review staged changes
./scripts/gemini-review.sh all security           # Security review of all changes
./scripts/gemini-review.sh commit performance     # Performance review of last commit

# Integrated workflow (optional step during completion)
./scripts/complete_issue.sh 69                    # Offers Gemini review choice
```

#### Review Output
- Detailed feedback with actionable recommendations
- Risk assessments and severity ratings
- Specific fix suggestions with examples
- Archived reviews in `reviews/` directory
- Interactive follow-up options

## Development Notes
- Game uses `a1`-`h8` coordinate notation
- Undo (`u`), redo (`r`), save (`s`), load (`l`) commands available in CLI
- GUI shows legal moves highlighting and real-time score display
- All tests can be run individually without pytest if needed
- AI difficulty affects both move selection algorithm and opening book usage