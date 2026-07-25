#!/bin/bash
#
# StarlyProxy Updater
# Check for updates and upgrade existing installation
#

set -e

INSTALL_DIR="/opt/starlyproxy"
REPO_URL="https://github.com/arimakomi/StarlyProxy.git"
CURRENT_VERSION=""
LATEST_VERSION=""

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
    ███████╗████████╗ █████╗ ██████╗ ██╗  ██╗   ██╗
    ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║  ╚██╗ ██╔╝
    ███████╗   ██║   ███████║██████╔╝██║   ╚████╔╝ 
    ╚════██║   ██║   ██╔══██║██╔══██╗██║    ╚██╔╝  
    ███████║   ██║   ██║  ██║██║  ██║███████╗██║   
    ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝   
                                                    
         StarlyProxy Updater                        
EOF
echo -e "${NC}"

# Check if installed
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}StarlyProxy is not installed.${NC}"
    echo "Run installer first: curl -fsSL https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/install.sh | sudo bash"
    exit 1
fi

echo "Checking for updates..."

# Get current version
cd "$INSTALL_DIR"
CURRENT_VERSION=$(git describe --tags --always 2>/dev/null || echo "unknown")

# Fetch latest
git fetch origin main >/dev/null 2>&1

# Get latest version
LATEST_VERSION=$(git describe --tags --always origin/main 2>/dev/null || echo "unknown")

echo "Current version: $CURRENT_VERSION"
echo "Latest version:  $LATEST_VERSION"

if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    echo -e "${GREEN}✓ Already up to date!${NC}"
    exit 0
fi

echo ""
read -p "Update to latest version? [Y/n]: " confirm

if [[ "$confirm" =~ ^[Nn]$ ]]; then
    echo "Update cancelled."
    exit 0
fi

echo ""
echo "Updating..."

# Stop service
echo "→ Stopping service..."
systemctl stop starlyproxy-panel 2>/dev/null || true

# Pull latest
echo "→ Downloading latest version..."
git pull origin main

# Update dependencies
echo "→ Updating dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt

# Restart service
echo "→ Restarting service..."
systemctl start starlyproxy-panel

echo ""
echo -e "${GREEN}✓ Update complete!${NC}"
echo "Updated from $CURRENT_VERSION to $LATEST_VERSION"
