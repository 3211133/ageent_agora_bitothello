#!/bin/bash
# PR Review Automation Script
# Usage: ./scripts/check-reviews.sh [action] [pr_number]
#
# This script automates PR review management:
# 1. Check all open PRs for reviews
# 2. Analyze review feedback
# 3. Generate response templates
# 4. Track review resolution status
# 5. Automate common review responses

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
    echo -e "${BLUE}👁️  $1${NC}"
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
    echo -e "${CYAN}📝 $1${NC}"
    echo -e "${CYAN}══════════════════════════════════════════${NC}"
}

print_info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

# Check if GitHub CLI is available
check_gh_cli() {
    if ! command -v gh >/dev/null 2>&1; then
        print_error "GitHub CLI (gh) is not available. Please install it first."
        print_info "Install: https://cli.github.com/"
        exit 1
    fi
}

# Check environment
check_environment() {
    if [ ! -f "pyproject.toml" ] || [ ! -d "src/othello" ]; then
        print_error "Not in the correct project directory. Please run from the project root."
        exit 1
    fi
}

# List all open PRs with review status
list_prs() {
    print_header "Open Pull Requests Review Status"
    
    local prs=$(gh pr list --state open --json number,title,author,reviewDecision,isDraft,updatedAt --jq '.[]')
    
    if [ -z "$prs" ]; then
        print_info "No open pull requests found."
        return 0
    fi
    
    echo "$prs" | jq -r '
        "PR #" + (.number | tostring) + ": " + .title + 
        "\n  Author: " + .author.login +
        "\n  Status: " + (if .isDraft then "DRAFT" else "READY" end) +
        "\n  Review: " + (.reviewDecision // "PENDING") +
        "\n  Updated: " + (.updatedAt | split("T")[0]) +
        "\n"
    ' 2>/dev/null || {
        # Fallback if jq fails
        gh pr list --state open
    }
}

# Check specific PR for reviews
check_pr_reviews() {
    local pr_number=$1
    
    if [ -z "$pr_number" ]; then
        print_error "Please provide a PR number"
        return 1
    fi
    
    print_header "PR #$pr_number Review Analysis"
    
    # Get PR details
    print_step "Fetching PR details..."
    local pr_info=$(gh pr view "$pr_number" --json title,author,reviewDecision,reviews,state)
    
    if [ -z "$pr_info" ]; then
        print_error "Could not fetch PR #$pr_number"
        return 1
    fi
    
    # Extract basic info
    local title=$(echo "$pr_info" | jq -r '.title')
    local author=$(echo "$pr_info" | jq -r '.author.login')
    local decision=$(echo "$pr_info" | jq -r '.reviewDecision // "PENDING"')
    local state=$(echo "$pr_info" | jq -r '.state')
    
    echo "  Title: $title"
    echo "  Author: $author"
    echo "  State: $state"
    echo "  Review Decision: $decision"
    echo ""
    
    # Get review comments
    print_step "Fetching review comments..."
    local reviews=$(echo "$pr_info" | jq -r '.reviews[]')
    
    if [ -n "$reviews" ]; then
        echo "$reviews" | jq -r '
            "Reviewer: " + .author.login +
            "\nState: " + .state +
            "\nSubmitted: " + (.submittedAt | split("T")[0]) +
            (if .body and .body != "" then "\nComment: " + .body else "" end) +
            "\n" + ("─" * 50) + "\n"
        ' 2>/dev/null || echo "Could not parse review details"
    else
        print_info "No reviews found for this PR"
    fi
    
    # Check for specific review comments
    print_step "Checking for review comments on code..."
    gh pr view "$pr_number" --comments | grep -E "(review|comment|change|fix|update)" | head -10 || print_info "No specific review comments found"
    
    echo ""
    
    # Suggest actions based on review state
    case "$decision" in
        "APPROVED")
            print_success "PR is approved! Ready to merge."
            ;;
        "CHANGES_REQUESTED")
            print_warning "Changes requested. Action needed:"
            echo "  1. Review the feedback above"
            echo "  2. Make necessary changes"
            echo "  3. Use: ./scripts/check-reviews.sh respond $pr_number"
            ;;
        "PENDING")
            print_info "Review pending. You can:"
            echo "  1. Wait for reviewer feedback"
            echo "  2. Ping reviewers if needed"
            echo "  3. Check CI status: gh pr checks $pr_number"
            ;;
        *)
            print_info "Review status: $decision"
            ;;
    esac
}

# Generate response templates for common review scenarios
generate_response() {
    local pr_number=$1
    local response_type=${2:-"general"}
    
    print_header "Response Template Generator"
    
    case "$response_type" in
        "addressed")
            cat << 'EOF'
## Review Feedback Addressed

Thank you for the review! I've addressed the feedback as follows:

### Changes Made:
- [ ] Issue 1: [Description of fix]
- [ ] Issue 2: [Description of fix]
- [ ] Issue 3: [Description of fix]

### Testing:
- [ ] All existing tests pass
- [ ] Added new tests for edge cases mentioned
- [ ] Manual testing completed

### Additional Notes:
[Any additional context or explanations]

The changes are ready for re-review. Please let me know if you need any clarifications!

🤖 Generated with [Claude Code](https://claude.ai/code)
EOF
            ;;
        "disagree")
            cat << 'EOF'
## Response to Review Feedback

Thank you for the review! I've carefully considered the feedback:

### Feedback Analysis:
1. **[Feedback Point 1]**: [Your analysis and reasoning]
2. **[Feedback Point 2]**: [Your analysis and reasoning]

### Decision Rationale:
I believe the current implementation is appropriate because:
- [Reason 1 with technical justification]
- [Reason 2 with reference to requirements/standards]
- [Reason 3 with consideration of alternatives]

### Alternative Considerations:
I considered the suggested approach but decided against it due to:
- [Technical constraint/consideration]
- [Performance/maintainability concern]
- [Compatibility requirement]

I'm happy to discuss this further or create a separate issue to track this as a future enhancement if you think it's valuable.

🤖 Generated with [Claude Code](https://claude.ai/code)
EOF
            ;;
        "partial")
            cat << 'EOF'
## Partial Response to Review Feedback

Thank you for the review! I've addressed some feedback and have thoughts on the rest:

### ✅ Addressed in this PR:
- [Item 1]: [Description of fix]
- [Item 2]: [Description of fix]

### 🔄 Will address in separate issue:
- [Complex item 1]: This requires significant changes that would be better handled in a separate PR
  - Created issue #[NUMBER] to track this
- [Complex item 2]: This touches multiple systems and needs broader discussion
  - Created issue #[NUMBER] to track this

### 💬 Discussion needed:
- [Item requiring discussion]: [Your thoughts and questions]

### Testing:
- [x] All tests pass with current changes
- [x] New issues created for deferred items

Let me know your thoughts on this approach!

🤖 Generated with [Claude Code](https://claude.ai/code)
EOF
            ;;
        *)
            cat << 'EOF'
## Review Response Template

Thank you for reviewing this PR! 

### Feedback Summary:
[Summarize the main points from the review]

### Response:
[Your detailed response to each point]

### Actions Taken:
- [ ] [Action 1]
- [ ] [Action 2]
- [ ] [Action 3]

### Testing:
- [ ] All tests pass
- [ ] Manual testing completed
- [ ] No regressions introduced

[Any additional notes or questions for the reviewer]

🤖 Generated with [Claude Code](https://claude.ai/code)
EOF
            ;;
    esac
    
    echo ""
    print_info "Template generated above. Copy and customize as needed."
    print_info "To post: gh pr comment $pr_number --body-file <template_file>"
}

# Post a response to a PR
respond_to_pr() {
    local pr_number=$1
    
    if [ -z "$pr_number" ]; then
        print_error "Please provide a PR number"
        return 1
    fi
    
    print_header "Responding to PR #$pr_number"
    
    # Check if there are any review comments to respond to
    local reviews=$(gh pr view "$pr_number" --json reviews --jq '.reviews[] | select(.state == "CHANGES_REQUESTED")')
    
    if [ -z "$reviews" ]; then
        print_info "No changes requested for this PR."
        return 0
    fi
    
    print_step "Detected changes requested. Options:"
    echo "  1. Make changes and address feedback"
    echo "  2. Generate response template"
    echo "  3. Create issues for complex feedback"
    echo ""
    
    read -p "Choose an action (1-3): " choice
    
    case "$choice" in
        "1")
            print_info "Make your changes, then run:"
            echo "  git add ."
            echo "  git commit -m 'Address PR review feedback'"
            echo "  git push"
            echo "  ./scripts/check-reviews.sh respond $pr_number"
            ;;
        "2")
            print_step "What type of response?"
            echo "  a) Addressed all feedback"
            echo "  b) Disagree with some feedback"
            echo "  c) Partial - some addressed, some deferred"
            echo ""
            read -p "Choose response type (a-c): " resp_type
            
            case "$resp_type" in
                "a") generate_response "$pr_number" "addressed" ;;
                "b") generate_response "$pr_number" "disagree" ;;
                "c") generate_response "$pr_number" "partial" ;;
                *) generate_response "$pr_number" "general" ;;
            esac
            ;;
        "3")
            print_info "Create new issues for complex feedback using:"
            echo "  gh issue create --title 'Follow-up: [Description]' --body '[Details from PR feedback]'"
            ;;
        *)
            print_info "No action taken."
            ;;
    esac
}

# Check CI status for PRs
check_ci_status() {
    print_header "CI Status for Open PRs"
    
    local prs=$(gh pr list --state open --json number,title)
    
    if [ -z "$prs" ]; then
        print_info "No open pull requests found."
        return 0
    fi
    
    echo "$prs" | jq -r '.[] | .number' | while read pr_number; do
        echo ""
        print_step "PR #$pr_number CI Status:"
        gh pr checks "$pr_number" --required 2>/dev/null || print_warning "Could not fetch CI status for PR #$pr_number"
    done
}

# Show help
show_help() {
    echo "PR Review Automation Script"
    echo ""
    echo "Usage: $0 [action] [pr_number]"
    echo ""
    echo "Actions:"
    echo "  list                    - List all open PRs with review status"
    echo "  check <pr_number>       - Check specific PR for reviews and comments"
    echo "  respond <pr_number>     - Interactive response helper for PR feedback"
    echo "  template <pr_number> <type> - Generate response templates"
    echo "                           Types: addressed, disagree, partial, general"
    echo "  ci                      - Check CI status for all open PRs"
    echo "  help                    - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 list                           # List all open PRs"
    echo "  $0 check 75                       # Check PR #75 for reviews"
    echo "  $0 respond 75                     # Interactive response for PR #75"
    echo "  $0 template 75 addressed          # Generate 'addressed' response template"
    echo "  $0 ci                             # Check CI status for all PRs"
    echo ""
    echo "💡 Workflow:"
    echo "  1. Run 'list' to see all open PRs"
    echo "  2. Run 'check <pr>' to analyze specific PR reviews"
    echo "  3. Address feedback in code"
    echo "  4. Run 'respond <pr>' to generate appropriate response"
    echo "  5. Use 'ci' to monitor build status"
}

# Main script logic
check_gh_cli
check_environment

if [ $# -eq 0 ]; then
    list_prs
    exit 0
fi

ACTION=$1
PR_NUMBER=$2
TEMPLATE_TYPE=$3

case "$ACTION" in
    "list")
        list_prs
        ;;
    "check")
        check_pr_reviews "$PR_NUMBER"
        ;;
    "respond")
        respond_to_pr "$PR_NUMBER"
        ;;
    "template")
        generate_response "$PR_NUMBER" "$TEMPLATE_TYPE"
        ;;
    "ci")
        check_ci_status
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