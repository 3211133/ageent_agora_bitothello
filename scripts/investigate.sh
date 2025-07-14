#!/bin/bash
# Investigation Automation Script
# Usage: ./scripts/investigate.sh <search_type> <search_term> [scope]
#
# This script automates code investigation and analysis:
# 1. Smart search across codebase
# 2. Related file discovery
# 3. Git history analysis
# 4. Dependency mapping
# 5. Impact assessment

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}🔍 $1${NC}"
}

print_result() {
    echo -e "${GREEN}📋 $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_header() {
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
    echo -e "${CYAN}🔎 $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
}

# Check arguments
if [ $# -lt 2 ]; then
    echo -e "${RED}❌ Usage: $0 <search_type> <search_term> [scope]${NC}"
    echo ""
    echo "Search Types:"
    echo "  function    - Find function definitions and usages"
    echo "  class       - Find class definitions and usages"
    echo "  variable    - Find variable definitions and usages"
    echo "  import      - Find import statements and dependencies"
    echo "  error       - Find error handling patterns"
    echo "  security    - Find security-related code patterns"
    echo "  performance - Find performance-related code"
    echo "  test        - Find test-related code"
    echo "  keyword     - General keyword search"
    echo ""
    echo "Scope (optional):"
    echo "  src         - Search only source code (default)"
    echo "  tests       - Search only test files"
    echo "  all         - Search all files"
    echo ""
    echo "Examples:"
    echo "  $0 function \"choose_move\" src"
    echo "  $0 class \"BitBoard\" all"
    echo "  $0 security \"password|token|key\" src"
    echo "  $0 error \"Exception|Error\" tests"
    exit 1
fi

SEARCH_TYPE=$1
SEARCH_TERM=$2
SCOPE=${3:-"src"}

# Set search paths based on scope
case "$SCOPE" in
    "src")
        SEARCH_PATHS="src/"
        ;;
    "tests")
        SEARCH_PATHS="tests/"
        ;;
    "all")
        SEARCH_PATHS="src/ tests/ scripts/"
        ;;
    *)
        echo -e "${RED}❌ Invalid scope: $SCOPE${NC}"
        exit 1
        ;;
esac

print_header "Investigating: $SEARCH_TERM (Type: $SEARCH_TYPE, Scope: $SCOPE)"

# Ensure we're in the correct directory
if [ ! -f "pyproject.toml" ] || [ ! -d "src/othello" ]; then
    echo -e "${RED}❌ Not in the correct project directory. Please run from the project root.${NC}"
    exit 1
fi

# Helper function to perform searches
perform_search() {
    local pattern=$1
    local description=$2
    local additional_options=${3:-""}
    
    print_step "$description"
    echo ""
    
    if command -v rg >/dev/null 2>&1; then
        # Use ripgrep if available (faster)
        if rg $additional_options "$pattern" $SEARCH_PATHS 2>/dev/null | head -20; then
            echo ""
        else
            echo "  (No matches found)"
            echo ""
        fi
    else
        # Fallback to grep
        if grep -r $additional_options "$pattern" $SEARCH_PATHS 2>/dev/null | head -20; then
            echo ""
        else
            echo "  (No matches found)"
            echo ""
        fi
    fi
}

# Main search logic based on type
case "$SEARCH_TYPE" in
    "function")
        print_header "Function Analysis: $SEARCH_TERM"
        
        # Function definitions
        perform_search "def\s+$SEARCH_TERM\s*\(" "Function Definitions" "-n"
        
        # Function calls
        perform_search "$SEARCH_TERM\s*\(" "Function Calls" "-n"
        
        # Method calls (object.function)
        perform_search "\.$SEARCH_TERM\s*\(" "Method Calls" "-n"
        ;;
        
    "class")
        print_header "Class Analysis: $SEARCH_TERM"
        
        # Class definitions
        perform_search "class\s+$SEARCH_TERM" "Class Definitions" "-n"
        
        # Class instantiations
        perform_search "$SEARCH_TERM\s*\(" "Class Instantiations" "-n"
        
        # Inheritance
        perform_search "class.*\($SEARCH_TERM\)" "Inheritance (as parent)" "-n"
        perform_search "class\s+$SEARCH_TERM.*\(" "Inheritance (as child)" "-n"
        ;;
        
    "variable")
        print_header "Variable Analysis: $SEARCH_TERM"
        
        # Variable assignments
        perform_search "$SEARCH_TERM\s*=" "Variable Assignments" "-n"
        
        # Variable usage
        perform_search "\b$SEARCH_TERM\b" "Variable Usage" "-n"
        ;;
        
    "import")
        print_header "Import Analysis: $SEARCH_TERM"
        
        # Direct imports
        perform_search "import\s+.*$SEARCH_TERM" "Direct Imports" "-n"
        
        # From imports
        perform_search "from\s+.*$SEARCH_TERM" "From Imports" "-n"
        perform_search "from\s+$SEARCH_TERM" "Importing From Module" "-n"
        ;;
        
    "error")
        print_header "Error Handling Analysis: $SEARCH_TERM"
        
        # Exception definitions
        perform_search "class.*$SEARCH_TERM.*Exception" "Exception Definitions" "-n"
        
        # Raise statements
        perform_search "raise\s+.*$SEARCH_TERM" "Raise Statements" "-n"
        
        # Exception handling
        perform_search "except\s+.*$SEARCH_TERM" "Exception Handling" "-n"
        
        # Error logging
        perform_search "log.*$SEARCH_TERM" "Error Logging" "-n"
        ;;
        
    "security")
        print_header "Security Analysis: $SEARCH_TERM"
        
        # Security patterns
        perform_search "$SEARCH_TERM" "Security Patterns" "-n -i"
        
        # Input validation
        perform_search "input.*validation|validate.*input" "Input Validation" "-n -i"
        
        # Authentication/Authorization
        perform_search "auth|password|token|key|secret" "Auth Patterns" "-n -i"
        ;;
        
    "performance")
        print_header "Performance Analysis: $SEARCH_TERM"
        
        # Performance patterns
        perform_search "$SEARCH_TERM" "Performance Patterns" "-n -i"
        
        # Caching
        perform_search "cache|memoiz" "Caching Patterns" "-n -i"
        
        # Optimization
        perform_search "optimize|performance|speed|fast" "Optimization Patterns" "-n -i"
        ;;
        
    "test")
        print_header "Test Analysis: $SEARCH_TERM"
        
        # Test functions
        perform_search "def\s+test.*$SEARCH_TERM|def\s+.*$SEARCH_TERM.*test" "Test Functions" "-n"
        
        # Test classes
        perform_search "class.*Test.*$SEARCH_TERM|class.*$SEARCH_TERM.*Test" "Test Classes" "-n"
        
        # Assertions
        perform_search "assert.*$SEARCH_TERM" "Assertions" "-n"
        ;;
        
    "keyword")
        print_header "Keyword Search: $SEARCH_TERM"
        
        # General search
        perform_search "$SEARCH_TERM" "All Occurrences" "-n -i"
        ;;
        
    *)
        echo -e "${RED}❌ Unknown search type: $SEARCH_TYPE${NC}"
        exit 1
        ;;
esac

# Additional analysis
print_header "Additional Analysis"

# Git history related to search term
print_step "Git History Analysis"
echo ""
if git log --oneline --grep="$SEARCH_TERM" -10 2>/dev/null | head -10; then
    echo ""
else
    echo "  (No related commits found)"
    echo ""
fi

# File modification dates
print_step "Recently Modified Files (related to scope)"
echo ""
find $SEARCH_PATHS -name "*.py" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -10 | while read timestamp filepath; do
    date=$(date -d "@$timestamp" "+%Y-%m-%d %H:%M")
    echo "  $date - $filepath"
done 2>/dev/null || echo "  (Unable to get file modification dates)"
echo ""

# Code metrics for found files
print_step "Code Metrics Summary"
echo ""
total_py_files=$(find $SEARCH_PATHS -name "*.py" -type f | wc -l)
total_lines=$(find $SEARCH_PATHS -name "*.py" -type f -exec wc -l {} + 2>/dev/null | tail -n 1 | awk '{print $1}' || echo "unknown")
echo "  Python files in scope: $total_py_files"
echo "  Total lines of code: $total_lines"
echo ""

# Summary and recommendations
print_header "Investigation Summary"

print_result "Search completed for '$SEARCH_TERM' (type: $SEARCH_TYPE)"
print_result "Scope: $SCOPE ($SEARCH_PATHS)"

echo ""
echo "💡 Next Steps:"
echo "  1. Review the found occurrences above"
echo "  2. Analyze the git history for related changes"
echo "  3. Check recently modified files for context"
echo "  4. Consider running tests related to found code:"
echo "     source venv/bin/activate && pytest tests/ -k \"$SEARCH_TERM\" -v"
echo ""
echo "🔧 Additional Investigation Commands:"
echo "  • More detailed search: rg \"$SEARCH_TERM\" $SEARCH_PATHS -A 3 -B 3"
echo "  • Find test files: ./scripts/investigate.sh test \"$SEARCH_TERM\" tests"
echo "  • Check dependencies: ./scripts/investigate.sh import \"$SEARCH_TERM\" all"
echo ""
print_result "Investigation complete! 🎯"