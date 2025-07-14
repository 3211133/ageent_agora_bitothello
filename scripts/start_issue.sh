#!/bin/bash
# Issue Start Automation Script
# Usage: ./scripts/start_issue.sh <issue_number> "Issue Title" <priority> [additional_analysis]
#
# This script automates the complete issue start workflow:
# 1. Environment setup and validation
# 2. Branch creation and checkout
# 3. Issue analysis and investigation
# 4. Slack notification
# 5. Initial testing

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}🔷 $1${NC}"
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

# Check arguments
if [ $# -lt 3 ]; then
    print_error "Usage: $0 <issue_number> \"Issue Title\" <priority> [additional_analysis]"
    print_error "Example: $0 69 \"Test Coverage Issues\" \"MEDIUM\" \"focus_on_integration_tests\""
    exit 1
fi

ISSUE_NUMBER=$1
ISSUE_TITLE=$2
PRIORITY=$3
ADDITIONAL_ANALYSIS=${4:-""}

# Validate priority
if [[ ! "$PRIORITY" =~ ^(LOW|MEDIUM|HIGH|CRITICAL)$ ]]; then
    print_error "Priority must be one of: LOW, MEDIUM, HIGH, CRITICAL"
    exit 1
fi

print_step "Starting issue #${ISSUE_NUMBER}: ${ISSUE_TITLE}"

# Step 1: Environment Setup and Validation
print_step "Step 1: Environment Setup and Validation"

# Check if we're in the correct directory
if [ ! -f "pyproject.toml" ] || [ ! -d "src/othello" ]; then
    print_error "Not in the correct project directory. Please run from the project root."
    exit 1
fi

# Activate virtual environment
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

print_step "Activating virtual environment..."
source venv/bin/activate

# Ensure dependencies are installed
print_step "Checking dependencies..."
if ! pip show pytest >/dev/null 2>&1; then
    print_warning "Installing test dependencies..."
    pip install pytest pytest-cov
fi

if ! pip show -e . >/dev/null 2>&1; then
    print_warning "Installing package in development mode..."
    pip install -e .
fi

print_success "Environment setup complete"

# Step 2: Git Operations
print_step "Step 2: Git Operations"

# Ensure we're on main and up to date
print_step "Syncing with main branch..."
git checkout main
git pull origin main

# Create branch name from issue
BRANCH_NAME="fix/issue-${ISSUE_NUMBER}-$(echo "$ISSUE_TITLE" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')"

print_step "Creating branch: ${BRANCH_NAME}"

# Check if branch already exists
if git show-ref --verify --quiet refs/heads/"$BRANCH_NAME"; then
    print_warning "Branch $BRANCH_NAME already exists. Checking out existing branch..."
    git checkout "$BRANCH_NAME"
else
    git checkout -b "$BRANCH_NAME"
fi

print_success "Git operations complete"

# Step 3: Initial Testing
print_step "Step 3: Initial Testing (Baseline)"

print_step "Running baseline tests to ensure starting point is clean..."
if pytest --tb=short -q; then
    print_success "Baseline tests passing"
else
    print_error "Baseline tests failing! Please fix before proceeding."
    exit 1
fi

# Step 4: Issue Analysis
print_step "Step 4: Issue Analysis"

print_step "Fetching issue details from GitHub..."
if command -v gh >/dev/null 2>&1; then
    echo "Issue #${ISSUE_NUMBER} Details:"
    echo "=========================="
    gh issue view "$ISSUE_NUMBER" || print_warning "Could not fetch issue details from GitHub"
    echo "=========================="
else
    print_warning "GitHub CLI not available. Skipping issue detail fetch."
fi

# Perform additional analysis based on issue type
print_step "Performing issue-specific analysis..."

case "$ADDITIONAL_ANALYSIS" in
    "security")
        print_step "Security-focused analysis..."
        echo "Checking for potential security vulnerabilities..."
        grep -r "input\|user\|request\|network" src/ --include="*.py" | head -10 || true
        ;;
    "memory")
        print_step "Memory-focused analysis..."
        echo "Checking for potential memory issues..."
        grep -r "history\|cache\|list\|dict" src/ --include="*.py" | head -10 || true
        ;;
    "ai")
        print_step "AI-focused analysis..."
        echo "Checking AI module structure..."
        ls -la src/othello/ai.py || true
        grep -n "def.*choose_move\|def.*evaluate" src/othello/ai.py || true
        ;;
    "compatibility")
        print_step "Compatibility-focused analysis..."
        echo "Checking version and compatibility info..."
        grep -r "size\|version\|compat" src/ --include="*.py" | head -10 || true
        ;;
    *)
        print_step "General analysis..."
        echo "Project structure overview:"
        find src/ -name "*.py" -type f | head -10
        ;;
esac

print_success "Issue analysis complete"

# Step 5: Slack Notification
print_step "Step 5: Slack Notification"

if [ -f "./scripts/notify_issue_start.sh" ]; then
    print_step "Sending Slack notification..."
    ./scripts/notify_issue_start.sh "$ISSUE_NUMBER" "$ISSUE_TITLE" "$PRIORITY"
    print_success "Slack notification sent"
else
    print_warning "Slack notification script not found. Skipping notification."
fi

# Step 6: Summary and Next Steps
print_step "Step 6: Setup Complete - Ready to Work"

echo ""
echo "================================================"
print_success "Issue #${ISSUE_NUMBER} setup complete!"
echo "================================================"
echo ""
echo "📋 Summary:"
echo "  • Issue: #${ISSUE_NUMBER} - ${ISSUE_TITLE}"
echo "  • Priority: ${PRIORITY}"
echo "  • Branch: ${BRANCH_NAME}"
echo "  • Environment: Activated and validated"
echo "  • Tests: Baseline passing"
echo ""
echo "🚀 Next Steps:"
echo "  1. Investigate the issue using the analysis above"
echo "  2. Implement fixes with comprehensive testing"
echo "  3. Run tests: source venv/bin/activate && pytest --cov=src --cov-report=term-missing"
echo "  4. When ready, use: ./scripts/complete_issue.sh ${ISSUE_NUMBER}"
echo ""
echo "💡 Quick Commands:"
echo "  • Test all: source venv/bin/activate && pytest --cov=src --cov-report=term-missing"
echo "  • Test specific: source venv/bin/activate && pytest tests/test_specific.py -v"
echo "  • Git status: git status"
echo ""
print_success "Ready to start development! 🎯"