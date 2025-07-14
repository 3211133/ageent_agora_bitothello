#!/bin/bash
# Gemini API Setup Helper Script
# Usage: ./scripts/setup-gemini.sh
#
# This script helps set up Gemini API integration for code reviews

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}🔧 $1${NC}"
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
    echo -e "${CYAN}🤖 $1${NC}"
    echo -e "${CYAN}══════════════════════════════════════════${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_header "Gemini API Setup for Code Reviews"

echo ""
print_info "This script will help you set up Google's Gemini AI for automated code reviews."
echo ""

# Check if API key is already configured
if [ -n "$GEMINI_API_KEY" ]; then
    print_success "Gemini API key is already set in environment variables"
    echo "  Current key: ${GEMINI_API_KEY:0:10}..."
    echo ""
    read -p "Do you want to update it? (y/N): " update_key
    if [[ ! "$update_key" =~ ^[Yy]$ ]]; then
        print_info "Keeping existing API key"
        exit 0
    fi
elif [ -f "$HOME/.gemini_api_key" ]; then
    print_success "Gemini API key found in ~/.gemini_api_key"
    echo ""
    read -p "Do you want to update it? (y/N): " update_key
    if [[ ! "$update_key" =~ ^[Yy]$ ]]; then
        print_info "Keeping existing API key file"
        exit 0
    fi
elif [ -f ".env" ] && grep -q "GEMINI_API_KEY" .env; then
    print_success "Gemini API key found in .env file"
    echo ""
    read -p "Do you want to update it? (y/N): " update_key
    if [[ ! "$update_key" =~ ^[Yy]$ ]]; then
        print_info "Keeping existing .env configuration"
        exit 0
    fi
fi

echo ""
print_step "Getting your Gemini API key"
echo ""
echo "1. Visit: https://makersuite.google.com/app/apikey"
echo "2. Sign in with your Google account"
echo "3. Click 'Create API key'"
echo "4. Copy the generated API key"
echo ""

read -p "Have you obtained your API key? (y/N): " has_key

if [[ ! "$has_key" =~ ^[Yy]$ ]]; then
    print_info "Please get your API key first and run this script again"
    exit 0
fi

echo ""
read -p "Please enter your Gemini API key: " api_key

# Validate API key format (basic check)
if [ -z "$api_key" ]; then
    print_error "API key cannot be empty"
    exit 1
fi

if [ ${#api_key} -lt 30 ]; then
    print_error "API key seems too short. Please check and try again."
    exit 1
fi

echo ""
print_step "Choose storage method for your API key:"
echo ""
echo "1. Environment variable (current session only)"
echo "2. ~/.gemini_api_key file (persistent, user-specific)"
echo "3. .env file in project (persistent, project-specific)"
echo "4. ~/.bashrc (persistent, all sessions)"
echo ""
read -p "Choose option (1-4): " storage_method

case "$storage_method" in
    "1")
        export GEMINI_API_KEY="$api_key"
        print_success "API key set for current session"
        print_warning "Note: This will only work for the current terminal session"
        ;;
    "2")
        echo "$api_key" > "$HOME/.gemini_api_key"
        chmod 600 "$HOME/.gemini_api_key"
        print_success "API key saved to ~/.gemini_api_key"
        ;;
    "3")
        if [ -f ".env" ]; then
            # Remove existing GEMINI_API_KEY from .env
            grep -v "GEMINI_API_KEY" .env > .env.tmp && mv .env.tmp .env || true
        fi
        echo "GEMINI_API_KEY=$api_key" >> .env
        chmod 600 .env
        print_success "API key added to .env file"
        
        # Add .env to .gitignore if not already there
        if [ -f ".gitignore" ] && ! grep -q "\.env" .gitignore; then
            echo ".env" >> .gitignore
            print_info "Added .env to .gitignore"
        fi
        ;;
    "4")
        if ! grep -q "GEMINI_API_KEY" "$HOME/.bashrc"; then
            echo "export GEMINI_API_KEY=\"$api_key\"" >> "$HOME/.bashrc"
            print_success "API key added to ~/.bashrc"
            print_info "Run 'source ~/.bashrc' or restart your terminal to activate"
        else
            print_warning "GEMINI_API_KEY already exists in ~/.bashrc"
            print_info "Please update it manually if needed"
        fi
        ;;
    *)
        print_error "Invalid option. Please run the script again."
        exit 1
        ;;
esac

echo ""
print_step "Testing API connection..."

# Test the API key
if [ "$storage_method" = "2" ]; then
    export GEMINI_API_KEY=$(cat "$HOME/.gemini_api_key")
elif [ "$storage_method" = "3" ]; then
    export GEMINI_API_KEY=$(grep "GEMINI_API_KEY" .env | cut -d= -f2)
fi

test_response=$(curl -s -w "\n%{http_code}" \
    -H "Content-Type: application/json" \
    -d '{"contents":[{"parts":[{"text":"Hello, this is a test. Please respond with just: API connection successful"}]}]}' \
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${GEMINI_API_KEY}")

http_code=$(echo "$test_response" | tail -n1)
response_body=$(echo "$test_response" | head -n -1)

if [ "$http_code" = "200" ]; then
    print_success "API connection test successful!"
    if command -v jq >/dev/null 2>&1; then
        response_text=$(echo "$response_body" | jq -r '.candidates[0].content.parts[0].text' 2>/dev/null || echo "API responded correctly")
        print_info "Response: $response_text"
    fi
else
    print_error "API connection test failed (HTTP $http_code)"
    print_error "Response: $response_body"
    print_info "Please check your API key and try again"
    exit 1
fi

echo ""
print_header "Setup Complete!"
echo ""
print_success "Gemini API is now configured for code reviews"
echo ""
print_info "You can now use:"
echo "  • ./scripts/gemini-review.sh - Standalone code review"
echo "  • ./scripts/complete_issue.sh - Integrated workflow with optional Gemini review"
echo ""
print_info "Example usage:"
echo "  ./scripts/gemini-review.sh staged security"
echo "  ./scripts/gemini-review.sh all performance"
echo "  ./scripts/complete_issue.sh 69  # Will offer Gemini review option"
echo ""

# Make sure gemini-review.sh is executable
if [ -f "./scripts/gemini-review.sh" ]; then
    chmod +x ./scripts/gemini-review.sh
    print_success "Gemini review script is ready to use"
else
    print_warning "Gemini review script not found. Please ensure it's in ./scripts/gemini-review.sh"
fi

print_success "Setup completed successfully! 🎉"