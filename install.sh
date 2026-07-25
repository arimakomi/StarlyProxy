#!/bin/bash
#
# StarlyProxy v3.0 - Advanced Professional Installer
# Complete rewrite with enhanced error handling and port selection
#

set -e

INSTALL_DIR="/opt/starlyproxy"
REPO_URL="https://github.com/arimakomi/StarlyProxy.git"
VENV_DIR="$INSTALL_DIR/venv"
LOG_FILE="/tmp/starlyproxy-install.log"

# Configuration
DEFAULT_PORT=5000
PANEL_DOMAIN=""
PANEL_PORT=$DEFAULT_PORT
ENABLE_SSL=false
AUTO_PORT=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Logging
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
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              ███████╗████████╗ █████╗ ██████╗ ██╗  ██╗      ║
║              ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║  ██║      ║
║              ███████╗   ██║   ███████║██████╔╝██║  ██║      ║
║              ╚════██║   ██║   ██╔══██║██╔══██╗██║  ██║      ║
║              ███████║   ██║   ██║  ██║██║  ██║███████║      ║
║              ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝      ║
║                                                              ║
║                    StarlyProxy v3.0                          ║
║          Multi-Instance Proxy Management System              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

log "Installation started"

# Check interactive mode
if [ -t 0 ]; then
    INTERACTIVE=true
    log "Interactive mode detected"
else
    INTERACTIVE=false
    log "Non-interactive mode (piped)"
    echo -e "${YELLOW}⚠️  Non-interactive mode - using default configuration${NC}"
    echo -e "${CYAN}   For custom setup: wget https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/install.sh && sudo bash install.sh${NC}"
    echo ""
    sleep 2
fi

# Root check
if [ "$EUID" -ne 0 ]; then 
    error_exit "Root access required. Try: sudo bash $0"
fi
echo -e "${GREEN}✓ Root access confirmed${NC}"
log "Root check passed"

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
find_available_port() {
    local start_port=$1
    local port=$start_port
    while netstat -tuln 2>/dev/null | grep -q ":$port " || ss -tuln 2>/dev/null | grep -q ":$port "; do
        ((port++))
        if [ $port -gt 65535 ]; then
            return 1
        fi
    done
    echo $port
    return 0
}

# Interactive configuration
if [ "$INTERACTIVE" = true ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Configuration${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Domain
    read -p "Domain for web panel [leave empty for IP-only]: " PANEL_DOMAIN
    log "Domain: ${PANEL_DOMAIN:-IP-only}"
    
    # Port selection
    echo ""
    echo -e "${CYAN}Port Configuration:${NC}"
    echo "  1) Use default port (5000)"
    echo "  2) Choose custom port"
    echo "  3) Auto-detect available port"
    read -p "Select option [1-3, default: 1]: " port_choice
    
    case $port_choice in
        2)
            read -p "Enter custom port [1024-65535]: " custom_port
            if [ "$custom_port" -ge 1024 ] && [ "$custom_port" -le 65535 ] 2>/dev/null; then
                PANEL_PORT=$custom_port
                log "Custom port selected: $PANEL_PORT"
            else
                echo -e "${YELLOW}⚠️  Invalid port. Using default: 5000${NC}"
                PANEL_PORT=5000
            fi
            ;;
        3)
            echo -e "${CYAN}Searching for available port...${NC}"
            PANEL_PORT=$(find_available_port 5000)
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ Available port found: $PANEL_PORT${NC}"
                log "Auto-detected port: $PANEL_PORT"
            else
                echo -e "${YELLOW}⚠️  No available port. Using default: 5000${NC}"
                PANEL_PORT=5000
            fi
            ;;
        *)
            PANEL_PORT=5000
            log "Default port selected: $PANEL_PORT"
            ;;
    esac
    
    # SSL
    if [ ! -z "$PANEL_DOMAIN" ]; then
        echo ""
        read -p "Enable SSL with Let's Encrypt? [yes/no]: " ssl_choice
        if [[ "$ssl_choice" =~ ^[Yy] ]]; then
            ENABLE_SSL=true
            log "SSL enabled"
        fi
    fi
    
    # Summary
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  Configuration Summary${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    [ ! -z "$PANEL_DOMAIN" ] && echo "  Domain: ${PANEL_DOMAIN}" || echo "  Domain: IP-only"
    echo "  Port: ${PANEL_PORT}"
    echo "  SSL: $([ "$ENABLE_SSL" = true ] && echo 'Enabled' || echo 'Disabled')"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    read -p "Continue with installation? [yes/no]: " confirm
    if [[ ! "$confirm" =~ ^[Yy] ]]; then
        echo "Installation cancelled."
        log "Installation cancelled by user"
        exit 0
    fi
    echo ""
fi

# Start installation
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Installation Progress${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# [1/9] System packages
echo -e "${CYAN}[1/9]${NC} Installing system packages..."
log "Step 1: Installing system packages"

install_packages() {
    local retry=0
    local max_retries=3
    
    while [ $retry -lt $max_retries ]; do
        if [[ "$OS" =~ ^(ubuntu|debian)$ ]]; then
            export DEBIAN_FRONTEND=noninteractive
            
            echo -e "${CYAN}   → Updating package list...${NC}"
            if apt-get update -qq >> "$LOG_FILE" 2>&1; then
                echo -e "${CYAN}   → Installing packages...${NC}"
                apt-get install -y python3 python3-pip python3-venv git nginx \
                    build-essential python3-dev >> "$LOG_FILE" 2>&1 && \
                apt-get install -y certbot python3-certbot-nginx >> "$LOG_FILE" 2>&1 || true
                return 0
            fi
            
        elif [[ "$OS" =~ ^(centos|rhel|rocky|almalinux)$ ]]; then
            echo -e "${CYAN}   → Installing EPEL repository...${NC}"
            yum install -y epel-release >> "$LOG_FILE" 2>&1 || true
            
            echo -e "${CYAN}   → Installing core packages...${NC}"
            yum install -y python3 python3-pip python3-devel git gcc gcc-c++ make >> "$LOG_FILE" 2>&1 && \
            yum install -y nginx >> "$LOG_FILE" 2>&1 || true
            
            echo -e "${CYAN}   → Installing certbot (optional)...${NC}"
            yum install -y certbot python3-certbot-nginx >> "$LOG_FILE" 2>&1 || true
            return 0
        fi
        
        ((retry++))
        if [ $retry -lt $max_retries ]; then
            echo -e "${YELLOW}   ⚠️  Retry $retry/$max_retries...${NC}"
            sleep 2
        fi
    done
    
    return 1
}

if install_packages; then
    echo -e "${GREEN}✓ System packages installed${NC}"
    log "System packages installed successfully"
else
    error_exit "Failed to install system packages after 3 retries. Check $LOG_FILE"
fi

# [2/9] Create directory
echo -e "${CYAN}[2/9]${NC} Creating installation directory..."
log "Step 2: Creating directory"
mkdir -p "$INSTALL_DIR" >> "$LOG_FILE" 2>&1 || error_exit "Failed to create directory"
cd "$INSTALL_DIR" || error_exit "Failed to change directory"
echo -e "${GREEN}✓ Directory: ${INSTALL_DIR}${NC}"

# [3/9] Download source
echo -e "${CYAN}[3/9]${NC} Downloading source code..."
log "Step 3: Downloading source"

if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "${CYAN}   → Updating existing repository...${NC}"
    git pull -q origin main >> "$LOG_FILE" 2>&1 || true
else
    echo -e "${CYAN}   → Cloning repository...${NC}"
    if ! git clone -q "$REPO_URL" "$INSTALL_DIR" >> "$LOG_FILE" 2>&1; then
        # Retry without quiet
        git clone "$REPO_URL" "$INSTALL_DIR" >> "$LOG_FILE" 2>&1 || error_exit "Failed to clone repository"
    fi
fi
echo -e "${GREEN}✓ Source code ready${NC}"

# [4/9] Python virtual environment
echo -e "${CYAN}[4/9]${NC} Creating Python virtual environment..."
log "Step 4: Creating virtualenv"
python3 -m venv "$VENV_DIR" >> "$LOG_FILE" 2>&1 || error_exit "Failed to create virtualenv"
source "$VENV_DIR/bin/activate" || error_exit "Failed to activate virtualenv"
echo -e "${GREEN}✓ Virtual environment created${NC}"

# [5/9] Python packages
echo -e "${CYAN}[5/9]${NC} Installing Python packages..."
log "Step 5: Installing Python packages"
echo -e "${CYAN}   → Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel >> "$LOG_FILE" 2>&1 || {
    echo -e "${YELLOW}   ⚠️  Pip upgrade failed, continuing...${NC}"
    log "WARNING: pip upgrade failed"
}

echo -e "${CYAN}   → Installing core dependencies...${NC}"
pip install netifaces psutil pyyaml >> "$LOG_FILE" 2>&1 || error_exit "Failed to install core packages"

echo -e "${CYAN}   → Installing web framework...${NC}"
pip install "flask>=2.3.0" flask-cors >> "$LOG_FILE" 2>&1 || error_exit "Failed to install Flask"

echo -e "${CYAN}   → Installing optional packages...${NC}"
pip install colorama >> "$LOG_FILE" 2>&1 || {
    echo -e "${YELLOW}   ⚠️  Optional packages skipped${NC}"
    log "WARNING: colorama install failed"
}

echo -e "${GREEN}✓ Python packages installed${NC}"
log "Python packages installed successfully"

# [6/9] CLI setup
echo -e "${CYAN}[6/9]${NC} Setting up CLI command..."
log "Step 6: CLI setup"
ln -sf "$INSTALL_DIR/cli/starlyproxy-cli.py" /usr/local/bin/starlyproxy
chmod +x "$INSTALL_DIR/cli/starlyproxy-cli.py"
echo -e "${GREEN}✓ CLI command: ${CYAN}starlyproxy${NC}"

# [7/9] Database
echo -e "${CYAN}[7/9]${NC} Initializing database..."
log "Step 7: Database initialization"
python3 << PYCODE >> "$LOG_FILE" 2>&1 || error_exit "Failed to initialize database"
import sys
sys.path.insert(0, '$INSTALL_DIR')
from core import DatabaseManager
db = DatabaseManager()
print("Database initialized successfully")
PYCODE
echo -e "${GREEN}✓ Database initialized${NC}"

# Save configuration
cat > "$INSTALL_DIR/panel_config.json" << CONF
{
    "domain": "${PANEL_DOMAIN}",
    "port": ${PANEL_PORT},
    "ssl_enabled": ${ENABLE_SSL},
    "auto_port": ${AUTO_PORT},
    "installed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
CONF
log "Configuration saved"

# [8/9] Web server
echo -e "${CYAN}[8/9]${NC} Configuring web server..."
log "Step 8: Web server configuration"

if [ ! -z "$PANEL_DOMAIN" ]; then
    echo -e "${CYAN}   → Creating Nginx configuration...${NC}"
    cat > /etc/nginx/conf.d/starlyproxy.conf << 'NGINX'
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;
    
    location / {
        proxy_pass http://127.0.0.1:PORT_PLACEHOLDER;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
NGINX
    
    sed -i "s/DOMAIN_PLACEHOLDER/${PANEL_DOMAIN}/g" /etc/nginx/conf.d/starlyproxy.conf
    sed -i "s/PORT_PLACEHOLDER/${PANEL_PORT}/g" /etc/nginx/conf.d/starlyproxy.conf
    
    if nginx -t >> "$LOG_FILE" 2>&1; then
        systemctl enable nginx >> "$LOG_FILE" 2>&1 || true
        systemctl restart nginx >> "$LOG_FILE" 2>&1
        echo -e "${GREEN}   ✓ Nginx configured for: ${PANEL_DOMAIN}${NC}"
        log "Nginx configured successfully"
    else
        echo -e "${YELLOW}   ⚠️  Nginx configuration test failed${NC}"
        log "WARNING: Nginx test failed"
    fi
    
    if [ "$ENABLE_SSL" = true ] && command -v certbot >/dev/null; then
        echo -e "${CYAN}   → Obtaining SSL certificate...${NC}"
        if certbot --nginx -d "${PANEL_DOMAIN}" --non-interactive --agree-tos \
            --register-unsafely-without-email --redirect >> "$LOG_FILE" 2>&1; then
            echo -e "${GREEN}   ✓ SSL certificate obtained${NC}"
            log "SSL certificate obtained"
        else
            echo -e "${YELLOW}   ⚠️  SSL failed. Manual: sudo certbot --nginx -d ${PANEL_DOMAIN}${NC}"
            log "WARNING: SSL certificate failed"
        fi
    fi
else
    echo -e "${GREEN}✓ IP-only mode (no domain configuration)${NC}"
    log "IP-only mode selected"
fi

# [9/9] Systemd service
echo -e "${CYAN}[9/9]${NC} Creating systemd service..."
log "Step 9: Systemd service"

cat > /etc/systemd/system/starlyproxy-panel.service << SERVICE
[Unit]
Description=StarlyProxy Web Panel
Documentation=https://github.com/arimakomi/StarlyProxy
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR/panel
Environment="PATH=$VENV_DIR/bin"
Environment="FLASK_PORT=${PANEL_PORT}"
Environment="PYTHONUNBUFFERED=1"
ExecStart=$VENV_DIR/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload >> "$LOG_FILE" 2>&1
systemctl enable starlyproxy-panel >> "$LOG_FILE" 2>&1 || true
echo -e "${GREEN}✓ Service created and enabled${NC}"
log "Service created successfully"

# Final banner
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   ✅ Installation Completed Successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Access information
echo -e "${YELLOW}🚀 Start Panel:${NC}"
echo -e "   systemctl start starlyproxy-panel"
echo -e "   systemctl status starlyproxy-panel"
echo ""

echo -e "${CYAN}🌐 Access Panel:${NC}"
if [ ! -z "$PANEL_DOMAIN" ]; then
    if [ "$ENABLE_SSL" = true ]; then
        echo -e "   ${GREEN}https://${PANEL_DOMAIN}${NC}"
    else
        echo -e "   ${GREEN}http://${PANEL_DOMAIN}${NC}"
    fi
else
    SERVER_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
    if [ ! -z "$SERVER_IP" ]; then
        echo -e "   ${GREEN}http://${SERVER_IP}:${PANEL_PORT}${NC}"
    else
        echo -e "   ${GREEN}http://YOUR_SERVER_IP:${PANEL_PORT}${NC}"
    fi
fi
echo ""

echo -e "${YELLOW}📖 CLI Commands:${NC}"
echo -e "   ${CYAN}starlyproxy list${NC}              - List all instances"
echo -e "   ${CYAN}starlyproxy add ...${NC}           - Add new instance"
echo -e "   ${CYAN}starlyproxy start <name>${NC}     - Start instance"
echo -e "   ${CYAN}starlyproxy status <name>${NC}    - Check status"
echo ""

echo -e "${MAGENTA}📋 Installation log: ${LOG_FILE}${NC}"
echo ""
echo -e "${BLUE}🎉 Enjoy StarlyProxy!${NC}"
echo ""

log "Installation completed successfully"
