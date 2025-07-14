#!/bin/bash
# Quality Check Automation Script
# Usage: ./scripts/quality-check.sh [check_type] [scope]
#
# This script automates comprehensive quality checks:
# 1. Security vulnerability scanning
# 2. Performance analysis
# 3. Code quality metrics
# 4. Test coverage analysis
# 5. Dependency security audit

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
    echo -e "${BLUE}🔍 $1${NC}"
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
    echo -e "${CYAN}═══════════════════════════════════════════${NC}"
    echo -e "${CYAN}🛡️  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════${NC}"
}

print_info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

# Check environment
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
        source venv/bin/activate
    fi
}

# Security vulnerability scanning
security_scan() {
    print_header "Security Vulnerability Scan"
    
    activate_env
    
    # Check for common security patterns
    print_step "Scanning for security anti-patterns..."
    
    local security_issues=0
    
    # Check for hardcoded secrets
    print_step "Checking for hardcoded secrets..."
    if grep -r -i "password\s*=\|secret\s*=\|token\s*=\|key\s*=" src/ --include="*.py" | grep -v "test" | grep -v "example"; then
        print_warning "Potential hardcoded secrets found (review above)"
        ((security_issues++))
    else
        print_success "No hardcoded secrets detected"
    fi
    
    # Check for SQL injection patterns
    print_step "Checking for SQL injection vulnerabilities..."
    if grep -r "execute.*%\|query.*%\|sql.*%" src/ --include="*.py"; then
        print_warning "Potential SQL injection vulnerabilities found"
        ((security_issues++))
    else
        print_success "No SQL injection patterns detected"
    fi
    
    # Check for command injection patterns
    print_step "Checking for command injection vulnerabilities..."
    if grep -r "os\.system\|subprocess.*shell=True\|eval\|exec" src/ --include="*.py"; then
        print_warning "Potential command injection vulnerabilities found"
        ((security_issues++))
    else
        print_success "No command injection patterns detected"
    fi
    
    # Check for path traversal patterns
    print_step "Checking for path traversal vulnerabilities..."
    if grep -r "\.\./\|\.\.\\\\\" src/ --include="*.py"; then
        print_warning "Potential path traversal patterns found"
        ((security_issues++))
    else
        print_success "No path traversal patterns detected"
    fi
    
    # Check for insecure random usage
    print_step "Checking for insecure random number generation..."
    if grep -r "random\.random\|random\.choice" src/ --include="*.py" | grep -v "test" | grep -v "ai\.py"; then
        print_warning "Consider using secrets module for cryptographic randomness"
        ((security_issues++))
    else
        print_success "Random usage appears secure"
    fi
    
    # Network security checks
    print_step "Checking network security patterns..."
    if grep -r "socket\|urllib\|requests" src/ --include="*.py"; then
        print_info "Network code detected - review for proper error handling and timeouts"
    fi
    
    # Summary
    echo ""
    if [ $security_issues -eq 0 ]; then
        print_success "Security scan completed - no major issues found"
    else
        print_warning "Security scan completed - $security_issues potential issues found"
        print_info "Review the warnings above and address any real security concerns"
    fi
    
    return $security_issues
}

# Performance analysis
performance_check() {
    print_header "Performance Analysis"
    
    activate_env
    
    print_step "Analyzing algorithmic complexity..."
    
    # Check for nested loops that might indicate O(n²) or worse complexity
    print_step "Checking for nested loop patterns..."
    local nested_loops=$(grep -r "for.*:" src/ --include="*.py" -A 5 | grep -c "for.*:" || echo "0")
    if [ "$nested_loops" -gt 10 ]; then
        print_warning "High number of loops detected ($nested_loops) - review for optimization opportunities"
    else
        print_success "Loop complexity appears reasonable"
    fi
    
    # Check for recursive functions
    print_step "Checking for recursive functions..."
    if grep -r "def.*:" src/ --include="*.py" -A 10 | grep "return.*(" | grep -E "def\s+(\w+).*:.*return.*\1\("; then
        print_info "Recursive functions detected - ensure proper base cases and stack limits"
    else
        print_success "No obvious recursive patterns detected"
    fi
    
    # Check for large data structures
    print_step "Checking for large data structure patterns..."
    if grep -r "list.*\*\|dict.*\*\|\[\].*\*" src/ --include="*.py"; then
        print_info "Large data structure patterns detected - consider memory usage"
    fi
    
    # Memory usage patterns
    print_step "Checking for memory usage patterns..."
    if grep -r "cache\|memoiz\|LRU" src/ --include="*.py"; then
        print_success "Caching patterns detected - good for performance"
    fi
    
    # Run a basic performance test
    print_step "Running basic performance benchmark..."
    python3 -c "
import sys
import time
sys.path.insert(0, 'src')

try:
    from othello.board import BitBoard
    from othello.ai import choose_move
    
    # Test basic operations
    start_time = time.time()
    
    for _ in range(100):
        board = BitBoard.initial()
        move = choose_move(board, True, 'easy')
        board.apply_move(move, True)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    if elapsed < 1.0:
        print(f'✅ Performance: {elapsed:.3f}s for 100 operations (Good)')
    elif elapsed < 5.0:
        print(f'⚠️  Performance: {elapsed:.3f}s for 100 operations (Acceptable)')
    else:
        print(f'❌ Performance: {elapsed:.3f}s for 100 operations (Slow)')
        
except Exception as e:
    print(f'❌ Performance test failed: {e}')
" || print_warning "Performance benchmark failed"
    
    print_success "Performance analysis completed"
}

# Code quality metrics
code_quality() {
    print_header "Code Quality Analysis"
    
    activate_env
    
    # Check Python syntax
    print_step "Checking Python syntax..."
    local syntax_errors=0
    for file in $(find src/ tests/ -name "*.py"); do
        if ! python -m py_compile "$file" 2>/dev/null; then
            print_error "Syntax error in $file"
            ((syntax_errors++))
        fi
    done
    
    if [ $syntax_errors -eq 0 ]; then
        print_success "All Python files have valid syntax"
    else
        print_error "$syntax_errors files have syntax errors"
        return 1
    fi
    
    # Check for import issues
    print_step "Checking import statements..."
    python3 -c "
import sys
sys.path.insert(0, 'src')
errors = []

try:
    import othello.board
    import othello.game
    import othello.ai
    print('✅ Core module imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
" || return 1
    
    # Code complexity analysis
    print_step "Analyzing code complexity..."
    
    # Count lines of code
    local total_lines=$(find src/ -name "*.py" -exec wc -l {} + | tail -n 1 | awk '{print $1}')
    local total_files=$(find src/ -name "*.py" | wc -l)
    local avg_lines=$((total_lines / total_files))
    
    echo "  Total lines of code: $total_lines"
    echo "  Total Python files: $total_files"
    echo "  Average lines per file: $avg_lines"
    
    if [ $avg_lines -gt 200 ]; then
        print_warning "Average file size is large ($avg_lines lines) - consider refactoring"
    else
        print_success "File sizes are reasonable"
    fi
    
    # Check for very long functions
    print_step "Checking for long functions..."
    local long_functions=$(awk '/^def / { func_start=NR; func_name=$2 } /^def |^class |^$/ { if (func_start && NR-func_start > 50) print FILENAME":"func_start":"func_name" ("NR-func_start" lines)"; func_start=0 }' src/**/*.py | wc -l)
    
    if [ "$long_functions" -gt 0 ]; then
        print_warning "$long_functions functions are longer than 50 lines - consider breaking them down"
    else
        print_success "Function sizes are reasonable"
    fi
    
    # Check for TODO/FIXME comments
    print_step "Checking for TODO/FIXME comments..."
    local todos=$(grep -r "TODO\|FIXME\|XXX\|HACK" src/ --include="*.py" | wc -l)
    if [ "$todos" -gt 0 ]; then
        print_info "$todos TODO/FIXME comments found - consider addressing them"
        grep -r "TODO\|FIXME\|XXX\|HACK" src/ --include="*.py" | head -5
    else
        print_success "No TODO/FIXME comments found"
    fi
    
    print_success "Code quality analysis completed"
}

# Test coverage analysis
coverage_analysis() {
    print_header "Test Coverage Analysis"
    
    activate_env
    
    print_step "Running test coverage analysis..."
    
    # Generate coverage report
    if pytest --cov=src --cov-report=term-missing --cov-report=xml --tb=no -q; then
        print_success "Test suite passed"
        
        # Parse coverage report if available
        if [ -f "coverage.xml" ]; then
            # Extract coverage percentage from XML (basic parsing)
            local coverage=$(python3 -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('coverage.xml')
    root = tree.getroot()
    coverage = root.attrib.get('line-rate', '0')
    percentage = float(coverage) * 100
    print(f'{percentage:.1f}')
except:
    print('unknown')
" 2>/dev/null || echo "unknown")
            
            if [ "$coverage" != "unknown" ]; then
                if (( $(echo "$coverage > 80" | bc -l) )); then
                    print_success "Test coverage: ${coverage}% (Good)"
                elif (( $(echo "$coverage > 60" | bc -l) )); then
                    print_warning "Test coverage: ${coverage}% (Acceptable)"
                else
                    print_warning "Test coverage: ${coverage}% (Low - consider adding more tests)"
                fi
            fi
        fi
        
        # Check for untested files
        print_step "Checking for untested files..."
        if grep -E "TOTAL.*0%" coverage.xml 2>/dev/null; then
            print_warning "Some files have 0% coverage"
        fi
        
    else
        print_error "Test suite failed - fix failing tests first"
        return 1
    fi
    
    # Check test file ratio
    print_step "Analyzing test file ratio..."
    local src_files=$(find src/ -name "*.py" | wc -l)
    local test_files=$(find tests/ -name "*.py" | wc -l)
    local test_ratio=$(echo "scale=2; $test_files / $src_files" | bc -l 2>/dev/null || echo "0")
    
    echo "  Source files: $src_files"
    echo "  Test files: $test_files"
    echo "  Test ratio: $test_ratio"
    
    if (( $(echo "$test_ratio > 1.0" | bc -l 2>/dev/null || echo "0") )); then
        print_success "Good test file ratio"
    else
        print_info "Consider adding more test files for better coverage"
    fi
    
    print_success "Coverage analysis completed"
}

# Dependency security audit
dependency_audit() {
    print_header "Dependency Security Audit"
    
    activate_env
    
    print_step "Checking for security advisories..."
    
    # Check if safety is available
    if command -v safety >/dev/null 2>&1; then
        safety check --json || print_warning "Safety check found potential issues (see above)"
    else
        print_info "Safety tool not available - install with 'pip install safety' for dependency vulnerability scanning"
    fi
    
    # List installed packages
    print_step "Listing installed packages..."
    pip list --format=freeze | head -20
    
    # Check for common vulnerable packages (basic check)
    print_step "Checking for commonly vulnerable packages..."
    local vulnerable_patterns="urllib3.*1\.24\|requests.*2\.19\|jinja2.*2\.10"
    if pip list | grep -E "$vulnerable_patterns"; then
        print_warning "Potentially vulnerable package versions detected"
    else
        print_success "No obviously vulnerable packages detected"
    fi
    
    print_success "Dependency audit completed"
}

# Comprehensive quality check
comprehensive_check() {
    print_header "Comprehensive Quality Check"
    
    local total_issues=0
    
    # Run all checks
    echo ""
    security_scan || ((total_issues++))
    
    echo ""
    code_quality || ((total_issues++))
    
    echo ""
    coverage_analysis || ((total_issues++))
    
    echo ""
    performance_check
    
    echo ""
    dependency_audit
    
    echo ""
    print_header "Quality Check Summary"
    
    if [ $total_issues -eq 0 ]; then
        print_success "All quality checks passed! ✨"
        print_info "Your code meets the quality standards."
    else
        print_warning "$total_issues quality check(s) failed"
        print_info "Please address the issues above before proceeding."
    fi
    
    return $total_issues
}

# Show help
show_help() {
    echo "Quality Check Automation Script"
    echo ""
    echo "Usage: $0 [check_type] [scope]"
    echo ""
    echo "Check Types:"
    echo "  security     - Security vulnerability scanning"
    echo "  performance  - Performance analysis and benchmarks"
    echo "  quality      - Code quality metrics and analysis"
    echo "  coverage     - Test coverage analysis"
    echo "  deps         - Dependency security audit"
    echo "  all          - Run all quality checks (default)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all quality checks"
    echo "  $0 security           # Run only security scan"
    echo "  $0 coverage           # Run only coverage analysis"
    echo "  $0 quality            # Run only code quality checks"
    echo ""
    echo "💡 Integration with workflow:"
    echo "  • Run before committing changes"
    echo "  • Include in CI/CD pipeline"
    echo "  • Use during code reviews"
    echo "  • Regular project health checks"
}

# Main script logic
check_environment

if [ $# -eq 0 ]; then
    comprehensive_check
    exit $?
fi

CHECK_TYPE=$1

case "$CHECK_TYPE" in
    "security")
        security_scan
        ;;
    "performance")
        performance_check
        ;;
    "quality")
        code_quality
        ;;
    "coverage")
        coverage_analysis
        ;;
    "deps")
        dependency_audit
        ;;
    "all")
        comprehensive_check
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_error "Unknown check type: $CHECK_TYPE"
        echo ""
        show_help
        exit 1
        ;;
esac