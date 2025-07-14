#!/bin/bash
# Development Helper Script
# Usage: ./scripts/dev-helper.sh <action> [options]
#
# This script automates repetitive development tasks:
# 1. Quick testing with different scopes
# 2. Code quality checks
# 3. Watch mode for continuous testing
# 4. Smart commit assistance
# 5. Progress monitoring

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}⚡ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${CYAN}🛠️  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
}

print_info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

# Check if we're in the correct directory
check_environment() {
    if [ ! -f "pyproject.toml" ] || [ ! -d "src/othello" ]; then
        print_error "Not in the correct project directory. Please run from the project root."
        exit 1
    fi
    
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Please run ./scripts/start_issue.sh first."
        exit 1
    fi
}

# Activate virtual environment
activate_env() {
    if [ -z "$VIRTUAL_ENV" ]; then
        print_step "Activating virtual environment..."
        source venv/bin/activate
    fi
}

# Quick test function
quick_test() {
    local scope=${1:-"changed"}
    print_header "Quick Test: $scope"
    
    activate_env
    
    case "$scope" in
        "changed")
            print_step "Running tests for changed files only..."
            if git diff --name-only HEAD | grep -E "\.py$" | xargs -I {} pytest tests/ -k "$(basename {} .py)" -v --tb=short 2>/dev/null; then
                print_success "Changed file tests passed!"
            else
                print_warning "Running last failed tests instead..."
                pytest --lf -v --tb=short
            fi
            ;;
        "fast")
            print_step "Running fast tests (excluding slow ones)..."
            pytest tests/ -m "not slow" -x --tb=short
            ;;
        "unit")
            print_step "Running unit tests only..."
            pytest tests/test_board.py tests/test_game.py tests/test_ai.py -v --tb=short
            ;;
        "integration")
            print_step "Running integration tests..."
            pytest tests/test_game_integration.py tests/test_board_comprehensive.py -v --tb=short
            ;;
        "security")
            print_step "Running security-related tests..."
            pytest tests/ -k "security or path_traversal or memory" -v --tb=short
            ;;
        "all")
            print_step "Running all tests with coverage..."
            pytest --cov=src --cov-report=term-missing --tb=short
            ;;
        *)
            print_step "Running specific test pattern: $scope"
            pytest tests/ -k "$scope" -v --tb=short
            ;;
    esac
}

# Code quality check
quality_check() {
    print_header "Code Quality Check"
    
    activate_env
    
    print_step "Checking Python syntax..."
    find src/ tests/ -name "*.py" -exec python -m py_compile {} \; && print_success "Syntax check passed"
    
    print_step "Checking import statements..."
    if python -c "
import sys
sys.path.insert(0, 'src')
try:
    from othello import board, game, ai, cli
    print('✅ All imports working')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"; then
        print_success "Import check passed"
    else
        print_error "Import check failed"
        return 1
    fi
    
    print_step "Basic functionality test..."
    if python -c "
import sys
sys.path.insert(0, 'src')
from othello.board import BitBoard
from othello.game import Game
from othello.ai import choose_move
board = BitBoard.initial()
game = Game()
move = choose_move(board, True, 'easy')
print('✅ Basic functionality working')
"; then
        print_success "Functionality check passed"
    else
        print_error "Functionality check failed"
        return 1
    fi
}

# Watch mode for continuous testing
watch_mode() {
    local test_scope=${1:-"changed"}
    print_header "Watch Mode: $test_scope"
    
    print_info "Watching for file changes... (Press Ctrl+C to stop)"
    print_info "Test scope: $test_scope"
    
    # Check if inotify-tools is available
    if ! command -v inotifywait >/dev/null 2>&1; then
        print_warning "inotifywait not available. Using polling mode..."
        
        # Polling-based watch
        local last_check=$(date +%s)
        while true; do
            sleep 2
            local current_time=$(date +%s)
            
            # Check for modified files in the last 5 seconds
            if find src/ tests/ -name "*.py" -newermt "@$((current_time - 5))" 2>/dev/null | grep -q .; then
                if [ $current_time -gt $((last_check + 3)) ]; then  # Debounce
                    echo ""
                    print_step "Changes detected, running tests..."
                    quick_test "$test_scope" || true
                    last_check=$current_time
                    echo ""
                    print_info "Watching for more changes..."
                fi
            fi
        done
    else
        # inotify-based watch (more efficient)
        while inotifywait -q -r -e modify,create,delete --format '%w%f' src/ tests/ 2>/dev/null; do
            sleep 1  # Debounce
            echo ""
            print_step "Changes detected, running tests..."
            quick_test "$test_scope" || true
            echo ""
            print_info "Watching for more changes..."
        done
    fi
}

# Smart commit helper
commit_helper() {
    print_header "Smart Commit Helper"
    
    # Check for changes
    if [ -z "$(git status --porcelain)" ]; then
        print_warning "No changes to commit"
        return 0
    fi
    
    print_step "Current changes:"
    git status --short
    echo ""
    
    print_step "Running pre-commit checks..."
    
    # Quick quality check
    if ! quality_check; then
        print_error "Quality checks failed. Please fix issues before committing."
        return 1
    fi
    
    # Quick test
    print_step "Running quick tests..."
    if ! quick_test "fast"; then
        print_error "Tests failed. Please fix failing tests before committing."
        print_info "You can run './scripts/dev-helper.sh test all' for full test suite"
        return 1
    fi
    
    print_success "Pre-commit checks passed!"
    
    # Show detailed diff
    print_step "Detailed changes:"
    git diff --stat
    echo ""
    
    print_info "Ready to commit! Use 'git add' and 'git commit' when ready."
    print_info "Or use './scripts/complete_issue.sh <issue_number>' for full completion workflow."
}

# Progress monitoring
progress_monitor() {
    print_header "Development Progress Monitor"
    
    # Git status
    print_step "Git Status"
    git status --short
    echo ""
    
    # Current branch
    current_branch=$(git branch --show-current)
    print_step "Current Branch: $current_branch"
    echo ""
    
    # Recent commits
    print_step "Recent Commits"
    git log --oneline -5
    echo ""
    
    # Test status
    print_step "Quick Test Status"
    activate_env
    if pytest tests/test_board.py tests/test_game.py -q --tb=no 2>/dev/null; then
        print_success "Core tests passing"
    else
        print_warning "Some core tests failing"
    fi
    
    # File changes
    print_step "Modified Files"
    if [ -n "$(git status --porcelain)" ]; then
        git diff --name-only HEAD
    else
        echo "  No modified files"
    fi
    echo ""
    
    # Next steps
    print_step "Suggested Next Steps"
    if [ -n "$(git status --porcelain)" ]; then
        echo "  1. Review changes: git diff"
        echo "  2. Run tests: ./scripts/dev-helper.sh test all"
        echo "  3. Commit when ready: ./scripts/dev-helper.sh commit"
    else
        echo "  1. Make necessary changes"
        echo "  2. Use ./scripts/dev-helper.sh test <scope> to test"
        echo "  3. Use ./scripts/dev-helper.sh watch <scope> for continuous testing"
    fi
}

# Show help
show_help() {
    echo "Development Helper Script"
    echo ""
    echo "Usage: $0 <action> [options]"
    echo ""
    echo "Actions:"
    echo "  test <scope>    - Run tests with different scopes"
    echo "                    Scopes: changed, fast, unit, integration, security, all, <pattern>"
    echo ""
    echo "  quality         - Run code quality checks"
    echo ""
    echo "  watch <scope>   - Watch for file changes and run tests automatically"
    echo "                    Same scopes as test command"
    echo ""
    echo "  commit          - Smart commit helper with pre-commit checks"
    echo ""
    echo "  progress        - Show development progress and status"
    echo ""
    echo "  help            - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 test changed               # Test only changed files"
    echo "  $0 test security              # Run security-related tests"
    echo "  $0 watch fast                 # Watch mode with fast tests"
    echo "  $0 quality                    # Check code quality"
    echo "  $0 commit                     # Smart commit with checks"
    echo "  $0 progress                   # Show current progress"
    echo ""
    echo "💡 Tips:"
    echo "  • Use 'watch' mode during active development"
    echo "  • Run 'quality' before committing"
    echo "  • Use 'commit' for pre-commit validation"
    echo "  • Check 'progress' to see current status"
}

# Main script logic
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

ACTION=$1
shift  # Remove action from arguments

case "$ACTION" in
    "test")
        check_environment
        quick_test "${1:-changed}"
        ;;
    "quality")
        check_environment
        quality_check
        ;;
    "watch")
        check_environment
        watch_mode "${1:-changed}"
        ;;
    "commit")
        check_environment
        commit_helper
        ;;
    "progress")
        check_environment
        progress_monitor
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_error "Unknown action: $ACTION"
        echo ""
        show_help
        exit 1
        ;;
esac