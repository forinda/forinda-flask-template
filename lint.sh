#!/bin/bash
# Ruff linting and formatting script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running Ruff linter and formatter...${NC}\n"

# Run linter with auto-fix
echo -e "${YELLOW}Step 1: Running linter with auto-fix...${NC}"
if pipenv run ruff check --fix .; then
    echo -e "${GREEN}✓ Linting passed${NC}\n"
else
    echo -e "${RED}✗ Linting found issues${NC}\n"
fi

# Run formatter
echo -e "${YELLOW}Step 2: Running formatter...${NC}"
if pipenv run ruff format .; then
    echo -e "${GREEN}✓ Formatting complete${NC}\n"
else
    echo -e "${RED}✗ Formatting failed${NC}\n"
    exit 1
fi

# Show remaining issues
echo -e "${YELLOW}Step 3: Checking for remaining issues...${NC}"
if pipenv run ruff check . --statistics | head -20; then
    echo -e "\n${GREEN}✓ All checks complete${NC}"
else
    echo -e "\n${YELLOW}⚠ Some issues remain${NC}"
fi
