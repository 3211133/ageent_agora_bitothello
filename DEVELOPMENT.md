# 🛠️ Development Guide

Quick start guide for setting up and working with the Othello game development environment.

## 🚀 Quick Setup (New Developer)

```bash
# 1. Clone the repository
git clone <repository-url>
cd ageent_agora_bitothello

# 2. Run automated setup (one-time)
./scripts/dev-setup.sh

# 3. Activate environment and start coding
source activate_dev.sh

# 4. Verify everything works
./run_tests.sh
othello --ai-vs-ai
```

That's it! You're ready to develop.

## 📋 Daily Development Workflow

### Starting a Session
```bash
# Quick activation
source activate_dev.sh

# Or manual activation
source venv/bin/activate
```

### Testing Your Changes
```bash
# Run all tests
./run_tests.sh

# Run specific tests
./run_tests.sh tests/test_board.py -v

# Run with coverage
./run_tests.sh --cov=src --cov-report=html
```

### Testing the Game
```bash
# CLI game
othello --ai --ai-level expert

# GUI version
othello-gui --vs-ai

# AI vs AI demo
othello --ai-vs-ai --size 6
```

## 🔧 Development Scripts

### Environment Management
- `./scripts/dev-setup.sh` - One-time development environment setup
- `source activate_dev.sh` - Quick environment activation
- `./run_tests.sh` - Quick test runner with auto-activation

### Issue Workflow
- `./scripts/start_issue.sh <number> "Title" <priority>` - Start working on an issue
- `./scripts/complete_issue.sh <number>` - Complete and create PR
- `./scripts/dev-helper.sh` - Development workflow helpers

### Code Quality
- `./scripts/quality-check.sh` - Comprehensive quality checks
- `./scripts/check-reviews.sh` - PR review management
- `./scripts/gemini-review.sh` - AI-powered code review

## 📁 Project Structure

```
ageent_agora_bitothello/
├── src/othello/           # Main package source
│   ├── board.py          # Bitboard implementation
│   ├── game.py           # Game state management
│   ├── ai.py             # AI algorithms
│   ├── cli.py            # Command-line interface
│   ├── gui.py            # Tkinter GUI
│   └── network.py        # Network play
├── tests/                # Test suite
├── scripts/              # Automation scripts
├── activate_dev.sh       # Quick environment activation
├── run_tests.sh          # Quick test runner
├── CLAUDE.md             # Full development documentation
└── DEVELOPMENT.md        # This file
```

## 🧪 Testing

### Test Categories
- **Unit Tests**: `test_board.py`, `test_game.py`, `test_ai.py`
- **Integration Tests**: `test_game_integration.py`
- **Comprehensive Tests**: `test_board_comprehensive.py`
- **Coverage Tests**: `test_*_coverage.py`
- **Security Tests**: `test_path_traversal_security.py`

### Running Tests
```bash
# All tests with coverage
./run_tests.sh

# Specific test file
./run_tests.sh tests/test_board.py

# Specific test function
./run_tests.sh tests/test_board.py::test_initial_board

# Watch mode (using dev-helper)
./scripts/dev-helper.sh watch fast
```

## 🔍 Debugging

### Common Issues

**Import Errors**
```bash
# Ensure package is installed in development mode
source venv/bin/activate
pip install -e .
```

**Missing Dependencies**
```bash
# Reinstall dependencies
./scripts/dev-setup.sh
```

**Test Failures**
```bash
# Run with verbose output
./run_tests.sh -v

# Run single failing test
./run_tests.sh tests/test_board.py::test_failing_function -v
```

### Debug Mode
```python
# Add to code for debugging
import sys
sys.path.append('src')

from othello.board import BitBoard
board = BitBoard.initial()
print(f"Debug: {board}")
```

## 🏗️ Building and Installation

### Development Mode (Recommended)
```bash
# Install in development mode (editable)
pip install -e .

# Changes to source code are immediately available
```

### Production Installation
```bash
# Install from source
pip install .

# Or build wheel
python -m build
pip install dist/othello-*.whl
```

## 📦 Dependencies

### Runtime Dependencies
- Python 3.8+
- Standard library only (no external dependencies)

### Development Dependencies
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting

### Optional Development Tools
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking

## 🚀 Performance Tips

### Fast Development Cycle
```bash
# Use watch mode for continuous testing
./scripts/dev-helper.sh watch fast

# Run only changed files
./scripts/dev-helper.sh test changed

# Quick syntax check
python -m py_compile src/othello/*.py
```

### Profiling
```bash
# Profile game performance
python -m cProfile -o profile.stats -c "
import sys; sys.path.append('src')
from othello.cli import run_game
run_game(ai_vs_ai=True, ai_level='expert', size=4)
"

# Analyze results
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(10)
"
```

## 🆘 Getting Help

### Documentation
- `CLAUDE.md` - Comprehensive development documentation
- `README.md` - Project overview and usage
- Code comments and docstrings

### Quick Tests
```bash
# Verify setup
python -c "import othello.board; print('✅ Import OK')"

# Test entry points
othello --help
othello-gui --help

# Environment info
./scripts/dev-helper.sh info
```

### Troubleshooting
1. Check Python version: `python3 --version` (need 3.8+)
2. Verify virtual environment: `which python` (should show venv path)
3. Check package installation: `pip show othello`
4. Run environment setup: `./scripts/dev-setup.sh`

## 💡 Pro Tips

1. **Always use virtual environment** - Avoids dependency conflicts
2. **Run tests frequently** - Catch issues early
3. **Use automation scripts** - Saves time and ensures consistency
4. **Check coverage** - Aim for >90% test coverage
5. **Profile performance** - AI moves should be fast (<100ms)

Happy coding! 🎉