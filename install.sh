#!/bin/bash

# Gagiteck Assets Installation Script
# This script sets up the Gagiteck robots.txt repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_NAME="Gagiteck-AI-Saas-Agentic"
REPO_URL="https://github.com/ajaniethos-1/Gagiteck-AI-Saas-Agentic.git"
INSTALL_DIR="$HOME/$REPO_NAME"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Gagiteck Assets - robots.txt Deployment Setup          ║${NC}"
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}✗ Git is not installed. Please install Git first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Git is installed${NC}"

if ! command -v curl &> /dev/null; then
    echo -e "${RED}✗ curl is not installed. Please install curl first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ curl is installed${NC}"

echo ""

# Clone or update repository
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Repository already exists at $INSTALL_DIR${NC}"
    echo -e "${BLUE}Updating repository...${NC}"
    cd "$INSTALL_DIR"
    git fetch origin
    git pull origin main
    echo -e "${GREEN}✓ Repository updated${NC}"
else
    echo -e "${BLUE}Cloning repository to $INSTALL_DIR...${NC}"
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    echo -e "${GREEN}✓ Repository cloned${NC}"
fi

echo ""

# Display setup instructions
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Setup Complete!                                         ║${NC}"
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo ""
echo -e "${GREEN}Repository installed at: ${YELLOW}$INSTALL_DIR${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo -e "1. ${YELLOW}Enable GitHub Pages:${NC}"
echo -e "   - Go to: https://github.com/ajaniethos-1/Gagiteck-AI-Saas-Agentic/settings/pages"
echo -e "   - Set source to 'main' branch and '/' (root) folder"
echo -e "   - Save the settings"
echo ""
echo -e "2. ${YELLOW}Verify deployment:${NC}"
echo -e "   - Wait a few minutes for GitHub Pages to deploy"
echo -e "   - Visit: https://ajaniethos-1.github.io/Gagiteck-AI-Saas-Agentic/robots.txt"
echo ""
echo -e "3. ${YELLOW}Setup Cloudflare Worker (Optional):${NC}"
echo -e "   - Log in to Cloudflare Dashboard"
echo -e "   - Create a new Worker"
echo -e "   - Copy the worker script from README.md"
echo -e "   - Add route: www.gagiteck.com/robots.txt"
echo ""
echo -e "4. ${YELLOW}Verify final setup:${NC}"
echo -e "   - Test: https://www.gagiteck.com/robots.txt"
echo -e "   - Use Google Search Console to verify accessibility"
echo ""
echo -e "${GREEN}Installation complete! Check README.md for detailed instructions.${NC}"
echo ""
