#!/bin/bash
# Development Environment Setup Script
# Automates venv creation, dependency installation, and environment verification

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_step() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Header
echo ""
echo "🚀 ================================================"
echo "   Othello Development Environment Setup"
echo "================================================"
echo ""

# Step 1: Check Python version
print_step "Step 1: Checking Python version"

if ! command -v python3 >/dev/null 2>&1; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MAJOR" -eq 3 -a "$PYTHON_MINOR" -lt 8 ]; then
    print_error "Python 3.8+ required. Found: $PYTHON_VERSION"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Step 2: Virtual environment setup
print_step "Step 2: Setting up virtual environment"

if [ ! -d "venv" ]; then
    print_step "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Step 3: Activate virtual environment
print_step "Step 3: Activating virtual environment"

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    print_success "Virtual environment activated"
else
    print_error "Virtual environment activation script not found"
    exit 1
fi

# Step 4: Install/upgrade pip
print_step "Step 4: Upgrading pip"

python -m pip install --upgrade pip > /dev/null 2>&1
print_success "Pip upgraded to latest version"

# Step 5: Install package in development mode
print_step "Step 5: Installing package in development mode"

if [ -f "pyproject.toml" ]; then
    pip install -e . > /dev/null 2>&1
    print_success "Package installed in development mode"
else
    print_error "pyproject.toml not found"
    exit 1
fi

# Step 6: Install development dependencies
print_step "Step 6: Installing development dependencies"

pip install pytest pytest-cov > /dev/null 2>&1
print_success "Development dependencies installed"

# Step 7: Verify installation
print_step "Step 7: Verifying installation"

# Test basic import
if python -c "import othello.board; print('Import test: OK')" > /dev/null 2>&1; then
    print_success "Package import verification passed"
else
    print_error "Package import verification failed"
    exit 1
fi

# Test entry points
if command -v othello >/dev/null 2>&1; then
    print_success "CLI entry point 'othello' available"
else
    print_warning "CLI entry point 'othello' not found in PATH"
fi

if command -v othello-gui >/dev/null 2>&1; then
    print_success "GUI entry point 'othello-gui' available"
else
    print_warning "GUI entry point 'othello-gui' not found in PATH"
fi

# Step 8: Run quick test
print_step "Step 8: Running quick functionality test"

if python -c "
import sys
sys.path.append('src')
from othello.board import BitBoard
from othello.game import Game

# Test basic functionality
board = BitBoard.initial()
game = Game(board=board)
legal = game.legal_moves()

if legal > 0:
    print('Functionality test: OK')
else:
    raise Exception('No legal moves found')
" > /dev/null 2>&1; then
    print_success "Quick functionality test passed"
else
    print_error "Quick functionality test failed"
    exit 1
fi

# Step 9: Create development shortcuts
print_step "Step 9: Creating development shortcuts"

# Create activate script
cat > activate_dev.sh << 'EOF'
#!/bin/bash
# Quick development environment activation
# Usage: source activate_dev.sh

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Development environment activated"
    echo "   • Virtual environment: venv"
    echo "   • Python: $(python --version)"
    echo "   • Package: othello (development mode)"
    echo ""
    echo "🔧 Quick commands:"
    echo "   • Run game: othello"
    echo "   • Run GUI: othello-gui"
    echo "   • Run tests: pytest --cov=src"
    echo "   • Quick test: python -c \"import othello.board; print('OK')\""
    echo ""
else
    echo "❌ Virtual environment not found. Run ./scripts/dev-setup.sh first."
fi
EOF

chmod +x activate_dev.sh
print_success "Created activate_dev.sh for quick environment activation"

# Create test runner script
cat > run_tests.sh << 'EOF'
#!/bin/bash
# Quick test runner with environment activation
# Usage: ./run_tests.sh [test_args]

if [ ! -f "venv/bin/activate" ]; then
    echo "❌ Virtual environment not found. Run ./scripts/dev-setup.sh first."
    exit 1
fi

source venv/bin/activate

if [ $# -eq 0 ]; then
    # Default: run all tests with coverage
    pytest --cov=src --cov-report=term-missing
else
    # Pass arguments to pytest
    pytest "$@"
fi
EOF

chmod +x run_tests.sh
print_success "Created run_tests.sh for quick test execution"

# Step 10: Summary and next steps
print_step "Step 10: Setup complete!"

echo ""
echo "🎉 ================================================"
print_success "Development environment setup completed!"
echo "================================================"
echo ""
echo "📋 Environment Details:"
echo "  • Python version: $PYTHON_VERSION"
echo "  • Virtual environment: venv/"
echo "  • Package: othello (development mode)"
echo "  • Dependencies: pytest, pytest-cov"
echo ""
echo "🚀 Quick Start Commands:"
echo ""
echo "  # Activate environment (method 1)"
echo "  source activate_dev.sh"
echo ""
echo "  # Activate environment (method 2)"
echo "  source venv/bin/activate"
echo ""
echo "  # Run tests"
echo "  ./run_tests.sh"
echo ""
echo "  # Run game"
echo "  othello --ai"
echo ""
echo "  # Run GUI"
echo "  othello-gui"
echo ""
echo "📖 Development Workflow:"
echo "  1. Always activate venv first: source activate_dev.sh"
echo "  2. Make code changes"
echo "  3. Run tests: ./run_tests.sh"
echo "  4. Test game: othello --ai-vs-ai"
echo ""
echo "🔧 Available Scripts:"
echo "  • ./scripts/dev-setup.sh - This setup script"
echo "  • ./scripts/start_issue.sh - Start working on an issue"
echo "  • ./scripts/complete_issue.sh - Complete an issue"
echo "  • ./scripts/dev-helper.sh - Development workflow helpers"
echo "  • ./activate_dev.sh - Quick environment activation"
echo "  • ./run_tests.sh - Quick test runner"
echo ""
echo "✨ Setup completed successfully! Happy coding! ✨"
echo ""