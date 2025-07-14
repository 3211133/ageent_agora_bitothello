#!/bin/bash
# Gemini Pre-PR Review Script
# Usage: ./scripts/gemini-review.sh [scope] [focus_area]
#
# This script automates pre-PR code review using Google's Gemini AI:
# 1. Collects code changes and context
# 2. Generates comprehensive review prompts
# 3. Sends to Gemini API for analysis
# 4. Formats and presents review feedback
# 5. Provides actionable recommendations

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}🤖 $1${NC}"
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
    echo -e "${CYAN}══════════════════════════════════════════${NC}"
    echo -e "${CYAN}🧠 $1${NC}"
    echo -e "${CYAN}══════════════════════════════════════════${NC}"
}

print_info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

print_review() {
    echo -e "${BOLD}📝 $1${NC}"
}

# Check environment and requirements
check_environment() {
    if [ ! -f "pyproject.toml" ] || [ ! -d "src/othello" ]; then
        print_error "Not in the correct project directory. Please run from the project root."
        exit 1
    fi
    
    # Check for Gemini API key
    if [ -z "$GEMINI_API_KEY" ]; then
        if [ -f ".env" ] && grep -q "GEMINI_API_KEY" .env; then
            print_step "Loading Gemini API key from .env file..."
            export $(grep "GEMINI_API_KEY" .env | xargs)
        elif [ -f "$HOME/.gemini_api_key" ]; then
            print_step "Loading Gemini API key from ~/.gemini_api_key..."
            export GEMINI_API_KEY=$(cat "$HOME/.gemini_api_key")
        else
            print_error "Gemini API key not found!"
            print_info "Please set GEMINI_API_KEY environment variable or create ~/.gemini_api_key file"
            print_info "Get your API key from: https://makersuite.google.com/app/apikey"
            exit 1
        fi
    fi
    
    # Check for curl
    if ! command -v curl >/dev/null 2>&1; then
        print_error "curl is required but not installed."
        exit 1
    fi
    
    # Check for jq (optional but recommended)
    if ! command -v jq >/dev/null 2>&1; then
        print_warning "jq not found. Install for better JSON formatting: sudo apt install jq"
    fi
}

# Generate review prompt based on focus area
generate_review_prompt() {
    local focus_area=${1:-"general"}
    local changed_files="$2"
    local git_diff="$3"
    local issue_context="$4"
    
    case "$focus_area" in
        "security")
            cat << EOF
You are an expert security code reviewer. Please conduct a comprehensive security review of the following code changes.

FOCUS AREAS:
- Input validation and sanitization
- Path traversal vulnerabilities  
- Command injection possibilities
- SQL injection vulnerabilities
- Authentication and authorization flaws
- Cryptographic implementations
- Memory safety issues
- Error handling that might leak information
- Network security considerations

CONTEXT:
Issue: $issue_context
Changed Files: $changed_files

CODE CHANGES:
$git_diff

Please provide:
1. Security risk assessment (HIGH/MEDIUM/LOW)
2. Specific vulnerabilities found (if any)
3. Recommended fixes for each issue
4. Security best practices suggestions
5. Overall security impact assessment

Be thorough but concise. Focus on actionable feedback.
EOF
            ;;
        "performance")
            cat << EOF
You are an expert performance code reviewer. Please analyze the following code changes for performance implications.

FOCUS AREAS:
- Algorithmic complexity (Big O analysis)
- Memory usage patterns
- Caching opportunities
- Database query efficiency
- Loop optimizations
- Data structure choices
- Concurrency considerations
- I/O operations efficiency

CONTEXT:
Issue: $issue_context
Changed Files: $changed_files

CODE CHANGES:
$git_diff

Please provide:
1. Performance impact assessment
2. Complexity analysis of key algorithms
3. Memory usage concerns
4. Optimization opportunities
5. Potential performance regressions
6. Recommended improvements

Focus on measurable performance impacts and practical optimizations.
EOF
            ;;
        "maintainability")
            cat << EOF
You are an expert code maintainability reviewer. Please evaluate the following code changes for long-term maintainability.

FOCUS AREAS:
- Code readability and clarity
- Function and class design
- Documentation quality
- Testing coverage
- Error handling patterns
- Code duplication
- Naming conventions
- Module organization
- Technical debt implications

CONTEXT:
Issue: $issue_context
Changed Files: $changed_files

CODE CHANGES:
$git_diff

Please provide:
1. Maintainability score (1-10)
2. Code quality assessment
3. Areas needing documentation
4. Refactoring suggestions
5. Testing recommendations
6. Long-term sustainability concerns

Focus on making the code easier to understand, modify, and extend.
EOF
            ;;
        "general")
            cat << EOF
You are an expert code reviewer. Please conduct a comprehensive review of the following code changes.

REVIEW AREAS:
- Code correctness and logic
- Security vulnerabilities
- Performance implications  
- Maintainability and readability
- Testing adequacy
- Error handling
- Documentation quality
- Best practices adherence
- Potential bugs or edge cases

CONTEXT:
Issue: $issue_context
Changed Files: $changed_files

CODE CHANGES:
$git_diff

Please provide:
1. Overall code quality assessment
2. Critical issues that must be fixed
3. Suggestions for improvement
4. Security considerations
5. Performance implications
6. Testing recommendations
7. Documentation needs

Be constructive and specific. Prioritize issues by severity.
EOF
            ;;
        *)
            print_error "Unknown focus area: $focus_area"
            exit 1
            ;;
    esac
}

# Call Gemini API
call_gemini_api() {
    local prompt="$1"
    local max_retries=3
    local retry_count=0
    
    print_step "Sending code to Gemini for review..."
    
    while [ $retry_count -lt $max_retries ]; do
        # Prepare JSON payload
        local json_payload=$(jq -n \
            --arg prompt "$prompt" \
            '{
                "contents": [{
                    "parts": [{
                        "text": $prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048
                }
            }')
        
        # Make API call
        local response=$(curl -s -w "\n%{http_code}" \
            -H "Content-Type: application/json" \
            -d "$json_payload" \
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${GEMINI_API_KEY}")
        
        local http_code=$(echo "$response" | tail -n1)
        local response_body=$(echo "$response" | head -n -1)
        
        if [ "$http_code" = "200" ]; then
            # Extract text from response
            if command -v jq >/dev/null 2>&1; then
                echo "$response_body" | jq -r '.candidates[0].content.parts[0].text' 2>/dev/null || echo "$response_body"
            else
                # Fallback parsing without jq
                echo "$response_body" | grep -o '"text":"[^"]*"' | sed 's/"text":"//g' | sed 's/"$//g' | sed 's/\\n/\n/g'
            fi
            return 0
        else
            print_warning "API call failed (HTTP $http_code). Retry $((retry_count + 1))/$max_retries"
            if [ $retry_count -eq $((max_retries - 1)) ]; then
                print_error "Gemini API call failed after $max_retries attempts"
                print_error "Response: $response_body"
                return 1
            fi
            retry_count=$((retry_count + 1))
            sleep 2
        fi
    done
}

# Collect code changes
collect_changes() {
    local scope=${1:-"staged"}
    
    print_step "Collecting code changes for review..."
    
    case "$scope" in
        "staged")
            # Get staged changes
            if [ -z "$(git diff --cached --name-only)" ]; then
                print_warning "No staged changes found. Checking all changes..."
                scope="all"
            else
                echo "$(git diff --cached)"
                return 0
            fi
            ;;
        "all")
            # Get all changes (staged + unstaged)
            if [ -z "$(git diff HEAD --name-only)" ]; then
                print_error "No changes found to review"
                exit 1
            else
                echo "$(git diff HEAD)"
                return 0
            fi
            ;;
        "commit")
            # Get changes from last commit
            echo "$(git diff HEAD~1 HEAD)"
            return 0
            ;;
        *)
            print_error "Unknown scope: $scope. Use 'staged', 'all', or 'commit'"
            exit 1
            ;;
    esac
}

# Get issue context
get_issue_context() {
    local current_branch=$(git branch --show-current)
    local issue_number=""
    
    # Try to extract issue number from branch name
    if [[ "$current_branch" =~ fix/.*issue-([0-9]+) ]]; then
        issue_number="${BASH_REMATCH[1]}"
    elif [[ "$current_branch" =~ fix.*-([0-9]+) ]]; then
        issue_number="${BASH_REMATCH[1]}"
    fi
    
    if [ -n "$issue_number" ] && command -v gh >/dev/null 2>&1; then
        print_step "Fetching issue context for #$issue_number..."
        local issue_title=$(gh issue view "$issue_number" --json title --jq '.title' 2>/dev/null || echo "")
        local issue_body=$(gh issue view "$issue_number" --json body --jq '.body' 2>/dev/null || echo "")
        
        if [ -n "$issue_title" ]; then
            echo "Issue #$issue_number: $issue_title"
            echo ""
            echo "$issue_body" | head -5
        else
            echo "Working on branch: $current_branch"
        fi
    else
        echo "Working on branch: $current_branch"
    fi
}

# Format and display review results
format_review_results() {
    local review_text="$1"
    local focus_area="$2"
    
    print_header "Gemini Code Review Results ($focus_area)"
    
    echo ""
    print_review "Review Feedback:"
    echo ""
    echo "$review_text"
    echo ""
    
    # Extract action items if possible
    if echo "$review_text" | grep -qi "fix\|address\|change\|update\|recommend"; then
        print_header "Action Items Summary"
        echo "$review_text" | grep -i -E "(fix|address|change|update|recommend|should|must|need)" | head -10
        echo ""
    fi
    
    # Save review to file
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local review_file="reviews/gemini_review_${timestamp}_${focus_area}.md"
    
    mkdir -p reviews
    cat > "$review_file" << EOF
# Gemini Code Review - $(date)

**Focus Area:** $focus_area
**Branch:** $(git branch --show-current)
**Reviewer:** Gemini AI

## Review Results

$review_text

## Code Changes Reviewed

\`\`\`diff
$(collect_changes "staged" | head -50)
\`\`\`

---
Generated by Gemini Pre-PR Review Script
EOF
    
    print_success "Review saved to: $review_file"
}

# Main review workflow
run_review() {
    local scope=${1:-"staged"}
    local focus_area=${2:-"general"}
    
    print_header "Gemini Pre-PR Code Review"
    
    # Collect necessary information
    local changed_files=$(git diff --cached --name-only | tr '\n' ' ' || git diff HEAD --name-only | tr '\n' ' ')
    local git_diff=$(collect_changes "$scope")
    local issue_context=$(get_issue_context)
    
    if [ -z "$git_diff" ]; then
        print_error "No code changes found to review"
        exit 1
    fi
    
    print_info "Changed files: $changed_files"
    print_info "Focus area: $focus_area"
    echo ""
    
    # Generate review prompt
    local review_prompt=$(generate_review_prompt "$focus_area" "$changed_files" "$git_diff" "$issue_context")
    
    # Call Gemini API
    local review_results=$(call_gemini_api "$review_prompt")
    
    if [ $? -eq 0 ] && [ -n "$review_results" ]; then
        format_review_results "$review_results" "$focus_area"
        
        # Ask for user action
        echo ""
        print_step "Review completed. What would you like to do?"
        echo "  1. Address feedback and re-run review"
        echo "  2. Proceed with PR creation"
        echo "  3. Get another review with different focus"
        echo "  4. Save review and exit"
        echo ""
        read -p "Choose an option (1-4): " choice
        
        case "$choice" in
            "1")
                print_info "Please address the feedback and run the review again"
                print_info "Command: ./scripts/gemini-review.sh $scope $focus_area"
                ;;
            "2")
                print_success "Review approved. You can proceed with PR creation."
                print_info "Command: ./scripts/complete_issue.sh <issue_number>"
                ;;
            "3")
                echo ""
                print_step "Choose focus area for additional review:"
                echo "  security, performance, maintainability, general"
                read -p "Focus area: " new_focus
                run_review "$scope" "$new_focus"
                ;;
            "4")
                print_success "Review saved. Exiting."
                ;;
            *)
                print_info "Review completed. Check the results above."
                ;;
        esac
    else
        print_error "Failed to get review from Gemini"
        exit 1
    fi
}

# Show help
show_help() {
    echo "Gemini Pre-PR Review Script"
    echo ""
    echo "Usage: $0 [scope] [focus_area]"
    echo ""
    echo "Scope:"
    echo "  staged      - Review staged changes (default)"
    echo "  all         - Review all changes (staged + unstaged)"
    echo "  commit      - Review last commit"
    echo ""
    echo "Focus Area:"
    echo "  general     - Comprehensive review (default)"
    echo "  security    - Security-focused review"
    echo "  performance - Performance-focused review"
    echo "  maintainability - Maintainability-focused review"
    echo ""
    echo "Setup:"
    echo "  export GEMINI_API_KEY='your-api-key'"
    echo "  # OR create ~/.gemini_api_key file"
    echo "  # OR add GEMINI_API_KEY=your-key to .env file"
    echo ""
    echo "Examples:"
    echo "  $0                           # Review staged changes (general)"
    echo "  $0 all security              # Security review of all changes"
    echo "  $0 staged performance        # Performance review of staged changes"
    echo "  $0 commit maintainability    # Maintainability review of last commit"
    echo ""
    echo "Get API key: https://makersuite.google.com/app/apikey"
}

# Main script logic
check_environment

if [ $# -eq 0 ]; then
    run_review "staged" "general"
elif [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
else
    SCOPE=${1:-"staged"}
    FOCUS_AREA=${2:-"general"}
    run_review "$SCOPE" "$FOCUS_AREA"
fi