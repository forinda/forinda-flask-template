#!/bin/bash

# Script to generate .env file from .env.example
# Usage: ./generate_env.sh

ENV_FILE=".env"
EXAMPLE_FILE=".env.example"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Environment File Generator${NC}"
echo "================================"
echo ""

# Check if .env.example exists
if [ ! -f "$EXAMPLE_FILE" ]; then
    echo -e "${RED}Error: $EXAMPLE_FILE not found!${NC}"
    exit 1
fi

# Check if .env already exists
if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Warning: $ENV_FILE already exists!${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Copy .env.example to .env
cp "$EXAMPLE_FILE" "$ENV_FILE"

# Generate random secret key
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")

# Replace placeholders with generated values
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/your-secret-key-here-change-in-production/$SECRET_KEY/g" "$ENV_FILE"
    sed -i '' "s/your-jwt-secret-key-here/$JWT_SECRET_KEY/g" "$ENV_FILE"
else
    # Linux
    sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/g" "$ENV_FILE"
    sed -i "s/your-jwt-secret-key-here/$JWT_SECRET_KEY/g" "$ENV_FILE"
fi

echo -e "${GREEN}✓ Successfully created $ENV_FILE${NC}"
echo ""
echo "Generated values:"
echo "  - SECRET_KEY: $SECRET_KEY"
echo "  - JWT_SECRET_KEY: $JWT_SECRET_KEY"
echo ""
echo -e "${YELLOW}Note: Please review and update the following in $ENV_FILE:${NC}"
echo "  - Database connection string (DATABASE_URL)"
echo "  - Email credentials (MAIL_USERNAME, MAIL_PASSWORD)"
echo "  - Any external API keys"
echo ""
echo -e "${GREEN}Done!${NC}"
