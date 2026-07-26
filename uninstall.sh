#!/bin/bash
#
# StarlyProxy Uninstaller
# Complete removal of StarlyProxy installation
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

INSTALL_DIR="/opt/starlyproxy"
LOG_FILE="/tmp/starlyproxy-uninstall.log"

echo -e "${BLUE}"
cat << "EOF"

    ███████╗████████╗ █████╗ ██████╗ ██╗  ██╗   ██╗
    ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║  ╚██╗ ██╔╝
    ███████╗   ██║   ███████║██████╔╝██║   ╚████╔╝ 
    ╚════██║   ██║   ██╔══██║██╔══██╗██║    ╚██╔╝  
    ███████║   ██║   ██║  ██║██║  ██║███████╗██║   
    ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝   
                                                    
         StarlyProxy Uninstaller                    

EOF
echo -e "${NC}"

# Confirmation
echo -e "${YELLOW}⚠️  WARNING: This will completely remove StarlyProxy${NC}"
echo ""
echo "The following will be removed:"
echo "  • Installation directory: $INSTALL_DIR"
echo "  • Systemd service: starlyproxy-panel.service"
echo "  • CLI command: /usr/local/bin/starlyproxy"
echo "  • All instances and configurations"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${BLUE}Uninstallation cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${CYAN}Starting uninstallation...${NC}"
echo ""

# Log function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

log "=== StarlyProxy Uninstallation Started ==="

# [1/5] Stop service
echo -e "${CYAN}[1/5]${NC} Stopping service..."
if systemctl is-active --quiet starlyproxy-panel 2>/dev/null; then
    systemctl stop starlyproxy-panel >> "$LOG_FILE" 2>&1 || true
    echo -e "${GREEN}✓ Service stopped${NC}"
else
    echo -e "${YELLOW}⚠️  Service not running${NC}"
fi

# [2/5] Disable service
echo -e "${CYAN}[2/5]${NC} Disabling service..."
if systemctl is-enabled --quiet starlyproxy-panel 2>/dev/null; then
    systemctl disable starlyproxy-panel >> "$LOG_FILE" 2>&1 || true
    echo -e "${GREEN}✓ Service disabled${NC}"
else
    echo -e "${YELLOW}⚠️  Service not enabled${NC}"
fi

# [3/5] Remove service file
echo -e "${CYAN}[3/5]${NC} Removing service file..."
if [ -f /etc/systemd/system/starlyproxy-panel.service ]; then
    rm -f /etc/systemd/system/starlyproxy-panel.service
    systemctl daemon-reload >> "$LOG_FILE" 2>&1
    echo -e "${GREEN}✓ Service file removed${NC}"
else
    echo -e "${YELLOW}⚠️  Service file not found${NC}"
fi

# [4/5] Remove CLI command
echo -e "${CYAN}[4/5]${NC} Removing CLI command..."
if [ -L /usr/local/bin/starlyproxy ] || [ -f /usr/local/bin/starlyproxy ]; then
    rm -f /usr/local/bin/starlyproxy
    echo -e "${GREEN}✓ CLI command removed${NC}"
else
    echo -e "${YELLOW}⚠️  CLI command not found${NC}"
fi

# [5/5] Remove installation directory
echo -e "${CYAN}[5/5]${NC} Removing installation directory..."
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}   → Removing $INSTALL_DIR...${NC}"
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}✓ Installation directory removed${NC}"
else
    echo -e "${YELLOW}⚠️  Installation directory not found${NC}"
fi

log "=== StarlyProxy Uninstallation Completed ==="

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ StarlyProxy has been completely removed${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Log file: $LOG_FILE"
echo ""
echo -e "${BLUE}Thank you for using StarlyProxy!${NC}"
echo ""
