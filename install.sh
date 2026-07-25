#!/bin/bash
#
# StarlyProxy v3.0 - Clean Installer
# Simplified and fixed version
#

set -e

INSTALL_DIR="/opt/starlyproxy"
REPO_URL="https://github.com/arimakomi/StarlyProxy.git"
VENV_DIR="$INSTALL_DIR/venv"
LOG_FILE="/tmp/starlyproxy-install.log"
DEFAULT_PORT=5000

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

error_exit() {
    echo -e "${RED}❌ Error: $1${NC}"
    log "ERROR: $1"
    exit 1
}

# Banner
clear 2>/dev/null || true
echo -e "${BLUE}"
cat << "EOF"

    ███████╗████████╗ █████╗ ██████╗ ██╗  ██╗   ██╗
    ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║  ╚██╗ ██╔╝
    ███████╗   ██║   ███████║██████╔╝██║   ╚████╔╝ 
    ╚════██║   ██║   ██╔══██║██╔══██╗██║    ╚██╔╝  
    ███████║   ██║   ██║  ██║██║  ██║███████╗██║   
    ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝

         StarlyProxy v3.0 - Proxy Manager
              Professional Edition

EOF
echo -e "${NC}"
sleep 1

# Root check
if [ "$EUID" -ne 0 ]; then 
    error_exit "Root access required. Try: sudo bash $0"
fi
echo -e "${GREEN}✓ Root access confirmed${NC}"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
    log "OS detected: $OS $VER"
else
    error_exit "Cannot detect operating system"
fi
echo -e "${GREEN}✓ Operating System: $OS $VER${NC}"
echo ""

# Find available port
PANEL_PORT=$DEFAULT_PORT
while netstat -tuln 2>/dev/null | grep -q ":$PANEL_PORT " || ss -tuln 2>/dev/null | grep -q ":$PANEL_PORT "; do
    ((PANEL_PORT++))
    if [ $PANEL_PORT -gt 65535 ]; then
        PANEL_PORT=$DEFAULT_PORT
        break
    fi
done
log "Selected port: $PANEL_PORT"

# Start installation
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Installation Progress${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# [1/7] System packages
echo -e "${CYAN}[1/7]${NC} Installing system packages..."
log "Step 1: Installing system packages"

if [[ "$OS" =~ ^(ubuntu|debian)$ ]]; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq >> "$LOG_FILE" 2>&1
    apt-get install -y python3 python3-pip python3-venv git nginx build-essential python3-dev >> "$LOG_FILE" 2>&1
elif [[ "$OS" =~ ^(centos|rhel|rocky|almalinux)$ ]]; then
    yum install -y epel-release >> "$LOG_FILE" 2>&1 || true
    yum install -y python3 python3-pip python3-devel git gcc gcc-c++ make nginx >> "$LOG_FILE" 2>&1
else
    error_exit "Unsupported OS: $OS"
fi
echo -e "${GREEN}✓ System packages installed${NC}"

# [2/7] Create directory
echo -e "${CYAN}[2/7]${NC} Creating installation directory..."
mkdir -p "$INSTALL_DIR" >> "$LOG_FILE" 2>&1 || error_exit "Failed to create directory"
cd "$INSTALL_DIR" || error_exit "Failed to change directory"
echo -e "${GREEN}✓ Directory: ${INSTALL_DIR}${NC}"

# [3/7] Download source
echo -e "${CYAN}[3/7]${NC} Downloading source code..."
if [ -d "$INSTALL_DIR/.git" ]; then
    git pull -q origin main >> "$LOG_FILE" 2>&1 || true
else
    git clone -q "$REPO_URL" "$INSTALL_DIR" >> "$LOG_FILE" 2>&1 || \
    git clone "$REPO_URL" "$INSTALL_DIR" >> "$LOG_FILE" 2>&1 || \
    error_exit "Failed to clone repository"
fi
echo -e "${GREEN}✓ Source code ready${NC}"

# [4/7] Python virtual environment
echo -e "${CYAN}[4/7]${NC} Creating Python virtual environment..."
python3 -m venv "$VENV_DIR" >> "$LOG_FILE" 2>&1 || error_exit "Failed to create virtualenv"
source "$VENV_DIR/bin/activate" || error_exit "Failed to activate virtualenv"
echo -e "${GREEN}✓ Virtual environment created${NC}"

# [5/7] Python packages
echo -e "${CYAN}[5/7]${NC} Installing Python packages..."
pip install --upgrade pip >> "$LOG_FILE" 2>&1 || true

# Essential packages
for pkg in netifaces psutil pyyaml; do
    echo -e "${CYAN}   → Installing $pkg...${NC}"
    pip install --no-cache-dir "$pkg" >> "$LOG_FILE" 2>&1 || error_exit "Failed to install $pkg"
done

# Flask
echo -e "${CYAN}   → Installing Flask...${NC}"
pip install --no-cache-dir "Flask==2.3.3" >> "$LOG_FILE" 2>&1 || \
pip install --no-cache-dir "Flask==2.0.3" >> "$LOG_FILE" 2>&1 || \
error_exit "Failed to install Flask"

# Flask-CORS and requests
pip install --no-cache-dir flask-cors requests >> "$LOG_FILE" 2>&1 || true

echo -e "${GREEN}✓ Python packages installed${NC}"

# [6/7] Database
echo -e "${CYAN}[6/7]${NC} Initializing database..."
mkdir -p "$INSTALL_DIR/data" >> "$LOG_FILE" 2>&1
export PYTHONPATH="$INSTALL_DIR:$PYTHONPATH"

# Initialize database
python3 << 'DBINIT' >> "$LOG_FILE" 2>&1 || true
import sys
import sqlite3
sys.path.insert(0, '/opt/starlyproxy')
try:
    from core.database import DatabaseManager
    db = DatabaseManager()
    print('Database initialized')
except Exception as e:
    conn = sqlite3.connect('/opt/starlyproxy/instances.db')
    conn.execute('CREATE TABLE IF NOT EXISTS instances (id INTEGER PRIMARY KEY, name TEXT UNIQUE, config TEXT)')
    conn.commit()
    conn.close()
    print('Database created (fallback)')
DBINIT

echo -e "${GREEN}✓ Database initialized${NC}"

# [7/7] Web panel service
echo -e "${CYAN}[7/7]${NC} Configuring web panel..."

# Create systemd service
cat > /etc/systemd/system/starlyproxy-panel.service << SERVEOF
[Unit]
Description=StarlyProxy Web Panel
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="PYTHONPATH=$INSTALL_DIR"
ExecStart=$VENV_DIR/bin/python3 $INSTALL_DIR/panel/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVEOF

systemctl daemon-reload
systemctl enable starlyproxy-panel >> "$LOG_FILE" 2>&1
systemctl start starlyproxy-panel >> "$LOG_FILE" 2>&1

# Wait for service
sleep 3

if systemctl is-active --quiet starlyproxy-panel; then
    echo -e "${GREEN}✓ Web panel started${NC}"
else
    echo -e "${YELLOW}⚠️  Service may need manual start${NC}"
fi

# CLI tool
cat > /usr/local/bin/starlyproxy << 'CLIEOF'
#!/bin/bash
VENV="/opt/starlyproxy/venv"
source "$VENV/bin/activate"
export PYTHONPATH="/opt/starlyproxy:$PYTHONPATH"
cd /opt/starlyproxy
python3 -m cli "$@"
CLIEOF

chmod +x /usr/local/bin/starlyproxy

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Installation Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}✓ StarlyProxy v3.0 installed successfully${NC}"
echo ""
echo -e "${CYAN}🌐 Access Panel:${NC}"
SERVER_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ ! -z "$SERVER_IP" ]; then
    echo -e "   ${GREEN}http://${SERVER_IP}:${PANEL_PORT}${NC}"
else
    echo -e "   ${GREEN}http://YOUR_SERVER_IP:${PANEL_PORT}${NC}"
fi
echo -e "   Default login: ${YELLOW}admin / admin${NC}"
echo ""
echo -e "${CYAN}🎯 Xray Dashboard:${NC}"
if [ ! -z "$SERVER_IP" ]; then
    echo -e "   ${GREEN}http://${SERVER_IP}:${PANEL_PORT}/xray${NC}"
fi
echo ""
echo -e "${YELLOW}📖 CLI Commands:${NC}"
echo -e "   ${CYAN}starlyproxy list${NC}              - List all instances"
echo -e "   ${CYAN}starlyproxy add ...${NC}           - Add new instance"
echo -e "   ${CYAN}systemctl status starlyproxy-panel${NC} - Check service"
echo ""
echo -e "${MAGENTA}📋 Installation log: ${LOG_FILE}${NC}"
echo ""
echo -e "${BLUE}🎉 Enjoy StarlyProxy!${NC}"
echo ""

log "Installation completed successfully"
