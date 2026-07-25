#!/bin/bash
#
# StarlyProxy Enhanced Installer Script v3.0
# Installation with domain, port, and SSL configuration
#

set -e

INSTALL_DIR="/opt/starlyproxy"
REPO_URL="https://github.com/arimakomi/StarlyProxy.git"
VENV_DIR="$INSTALL_DIR/venv"

# Default values
DEFAULT_PORT=5000
PANEL_DOMAIN=""
PANEL_PORT=$DEFAULT_PORT
ENABLE_SSL=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
   _____ _             _         ____                       
  / ____| |           | |       |  _ \                      
 | (___ | |_ __ _ _ __| |_   _  | |_) | __ _ __  _ __ __ __ 
  \___ \| __/ _` | '__| | | | | |  _ < / _` |\ \/ / '__|\/ /
  ____) | || (_| | |  | | |_| | | |_) | (_| | >  <| |    >  < 
 |_____/ \__\__,_|_|  |_|\__, | |____/ \__,_|/_/\_\_|   /_/\_\
                          __/ |
                         |___/
                         
    StarlyProxy v3.0 - Multi-Instance Proxy Manager
    
EOF
echo -e "${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ This script must be run as root${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Root access confirmed${NC}"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo -e "${RED}❌ Cannot detect operating system${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Operating System: $OS $VER${NC}"

# Ask for configuration
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Web Panel Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

read -p "Enter domain for web panel (leave empty for IP-only): " PANEL_DOMAIN
read -p "Enter port [default: 5000]: " input_port
PANEL_PORT=${input_port:-$DEFAULT_PORT}

if [ ! -z "$PANEL_DOMAIN" ]; then
    read -p "Enable SSL with Let's Encrypt? (yes/no) [no]: " ssl_choice
    if [[ "$ssl_choice" == "yes" || "$ssl_choice" == "y" ]]; then
        ENABLE_SSL=true
        echo -e "${YELLOW}⚠️  SSL will be configured after installation${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Configuration:${NC}"
if [ ! -z "$PANEL_DOMAIN" ]; then
    echo -e "  Domain: ${PANEL_DOMAIN}"
else
    echo -e "  Domain: Not configured (IP-only)"
fi
echo -e "  Port: ${PANEL_PORT}"
echo -e "  SSL: $([ "$ENABLE_SSL" = true ] && echo 'Enabled' || echo 'Disabled')"
echo ""

read -p "Continue? (yes/no): " confirm
if [[ "$confirm" != "yes" && "$confirm" != "y" ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Install dependencies
echo ""
echo -e "${BLUE}📦 Installing system dependencies...${NC}"

if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
    apt-get update -qq
    apt-get install -y python3 python3-pip python3-venv git libpcap-dev \
        build-essential python3-dev nginx certbot python3-certbot-nginx >/dev/null 2>&1
elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]] || [[ "$OS" == "rocky" ]]; then
    yum install -y python3 python3-pip python3-devel git libpcap-devel \
        gcc gcc-c++ make nginx certbot python3-certbot-nginx >/dev/null 2>&1
else
    echo -e "${YELLOW}⚠️  Unknown OS${NC}"
fi

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create directory
echo ""
echo -e "${BLUE}📁 Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Clone repository
if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "${BLUE}🔄 Updating...${NC}"
    git pull origin main
else
    echo -e "${BLUE}📥 Downloading...${NC}"
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

echo -e "${GREEN}✓ Source code ready${NC}"

# Virtual environment
echo ""
echo -e "${BLUE}🐍 Creating Python environment...${NC}"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo -e "${GREEN}✓ Virtual environment created${NC}"

# Install Python packages
echo ""
echo -e "${BLUE}📦 Installing Python packages...${NC}"
pip install --upgrade pip setuptools wheel >/dev/null 2>&1
pip install -r requirements.txt >/dev/null 2>&1

echo -e "${GREEN}✓ Python packages installed${NC}"

# CLI symlink
echo ""
echo -e "${BLUE}🔗 Creating CLI symlink...${NC}"
ln -sf "$INSTALL_DIR/cli/starlyproxy-cli.py" /usr/local/bin/starlyproxy
chmod +x "$INSTALL_DIR/cli/starlyproxy-cli.py"

echo -e "${GREEN}✓ CLI available${NC}"

# Initialize database
echo ""
echo -e "${BLUE}💾 Initializing database...${NC}"
python3 << PYEOF
import sys
sys.path.insert(0, '$INSTALL_DIR')
from core import DatabaseManager
db = DatabaseManager()
print("Database initialized")
PYEOF

echo -e "${GREEN}✓ Database ready${NC}"

# Save config
cat > "$INSTALL_DIR/panel_config.json" << CONFEOF
{
    "domain": "${PANEL_DOMAIN}",
    "port": ${PANEL_PORT},
    "ssl_enabled": ${ENABLE_SSL}
}
CONFEOF

# Nginx configuration
if [ ! -z "$PANEL_DOMAIN" ]; then
    echo ""
    echo -e "${BLUE}🌐 Configuring Nginx...${NC}"
    
    cat > /etc/nginx/sites-available/starlyproxy << 'NGINXEOF'
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
    }
}
NGINXEOF

    sed -i "s/DOMAIN_PLACEHOLDER/${PANEL_DOMAIN}/g" /etc/nginx/sites-available/starlyproxy
    sed -i "s/PORT_PLACEHOLDER/${PANEL_PORT}/g" /etc/nginx/sites-available/starlyproxy
    
    ln -sf /etc/nginx/sites-available/starlyproxy /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    
    echo -e "${GREEN}✓ Nginx configured${NC}"
    
    # SSL
    if [ "$ENABLE_SSL" = true ]; then
        echo ""
        echo -e "${BLUE}🔒 Configuring SSL...${NC}"
        
        certbot --nginx -d "${PANEL_DOMAIN}" --non-interactive --agree-tos \
            --register-unsafely-without-email --redirect
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ SSL configured${NC}"
        else
            echo -e "${YELLOW}⚠️  SSL failed. Manual: sudo certbot --nginx -d ${PANEL_DOMAIN}${NC}"
        fi
    fi
fi

# Systemd service
echo ""
echo -e "${BLUE}🌐 Creating systemd service...${NC}"

cat > /etc/systemd/system/starlyproxy-panel.service << SERVICEEOF
[Unit]
Description=StarlyProxy Web Panel
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR/panel
Environment="PATH=$VENV_DIR/bin"
Environment="FLASK_PORT=${PANEL_PORT}"
ExecStart=$VENV_DIR/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

systemctl daemon-reload
systemctl enable starlyproxy-panel.service

echo -e "${GREEN}✓ Service created${NC}"

# Final
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Installation completed!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}🚀 Start panel:${NC} systemctl start starlyproxy-panel"

if [ ! -z "$PANEL_DOMAIN" ]; then
    if [ "$ENABLE_SSL" = true ]; then
        echo -e "${YELLOW}🌐 Access:${NC} https://${PANEL_DOMAIN}"
    else
        echo -e "${YELLOW}🌐 Access:${NC} http://${PANEL_DOMAIN}"
    fi
else
    echo -e "${YELLOW}🌐 Access:${NC} http://YOUR_IP:${PANEL_PORT}"
fi

echo ""
echo -e "${YELLOW}📖 CLI:${NC}"
echo -e "   starlyproxy list"
echo -e "   starlyproxy add <name> <type> <mode> <server> <key>"
echo -e "   starlyproxy start <name>"
echo ""
echo -e "${BLUE}🎉 Done!${NC}"
