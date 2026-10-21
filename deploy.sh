#!/bin/bash

# SQL Dumper Advanced - Quick Deploy Script
# Supports: Linux/Ubuntu, Windows (WSL), macOS

set -e

echo "⚡ SQL Dumper - Quick Deploy"
echo "=============================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
else
    OS="unknown"
fi

echo -e "${YELLOW}[*] Detected OS: $OS${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}[✓] Python $PYTHON_VERSION found${NC}"

# Create virtual environment
echo -e "${YELLOW}[*] Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}[✓] Virtual environment created${NC}"
else
    echo -e "${GREEN}[✓] Virtual environment already exists${NC}"
fi

# Activate venv
if [ "$OS" = "windows" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo -e "${GREEN}[✓] Virtual environment activated${NC}"

# Install dependencies
echo -e "${YELLOW}[*] Installing dependencies...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}[✓] Dependencies installed${NC}"

# Setup environment file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[*] Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}[✓] .env file created (update with your API key)${NC}"
fi

# Create necessary directories
mkdir -p logs templates

# Information
echo ""
echo -e "${GREEN}========== SETUP COMPLETE ==========${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file (if needed):"
echo "   - Set your API key"
echo "   - Configure security settings"
echo ""
echo "2. Run the application:"
echo ""
if [ "$OS" = "windows" ]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo "   python app.py"
echo ""
echo "3. Access at: http://localhost:5000"
echo ""
echo "Alternative - Docker deployment:"
echo "   docker-compose up -d"
echo "   Access at: http://localhost"
echo ""
echo -e "${GREEN}=====================================${NC}"
