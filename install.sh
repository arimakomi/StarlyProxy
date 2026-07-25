#!/bin/bash
#
# StarlyProxy v3.0 - Professional Installer
# Works both interactively and via curl | bash
#

set -e

INSTALL_DIR="/opt/starlyproxy"
REPO_URL="https://github.com/arimakomi/StarlyProxy.git"
VENV_DIR="$INSTALL_DIR/venv"

# Default configuration
DEFAULT_PORT=5000
PANEL_DOMAIN=""
PANEL_PORT=$DEFAULT_PORT
ENABLE_SSL=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Banner
clear 2>/dev/null || true
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

# Check if interactive (not piped from curl)
if [ -t 0 ]; then
    INTERACTIVE=true
else
    INTERACTIVE=false
    echo -e "${YELLOW}ℹ  Non-interactive mode detected${NC}"
    echo -e "${YELLOW}   Using default configuration (Port: ${DEFAULT_PORT}, No SSL)${NC}"
    echo -e "${CYAN}   For custom setup: wget https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/install.sh && sudo bash install.sh${NC}"
    echo ""
    sleep 3
fi

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Root access required${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Root access confirmed${NC}"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo -e "${RED}❌ Cannot detect OS${NC}"
    exit 1
fi
echo -e "${GREEN}✓ OS: $OS $VER${NC}"
echo ""

# Interactive configuration
if [ "$INTERACTIVE" = true ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Configuration${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    read -p "Domain (leave empty for IP-only): " PANEL_DOMAIN
    read -p "Port [default: 5000]: " input_port
    PANEL_PORT=${input_port:-$DEFAULT_PORT}
    
    if [ ! -z "$PANEL_DOMAIN" ]; then
        read -p "Enable SSL with Let's Encrypt? [yes/no]: " ssl_choice
        if [[ "$ssl_choice" =~ ^[Yy] ]]; then
            ENABLE_SSL=true
        fi
    fi
    
    echo ""
    echo -e "${GREEN}Configuration:${NC}"
    [ ! -z "$PANEL_DOMAIN" ] && echo "  Domain: ${PANEL_DOMAIN}" || echo "  Domain: IP-only"
    echo "  Port: ${PANEL_PORT}"
    echo "  SSL: $([ "$ENABLE_SSL" = true ] && echo 'Yes' || echo 'No')"
    echo ""
    
    read -p "Continue? [yes/no]: " confirm
    if [[ ! "$confirm" =~ ^[Yy] ]]; then
        echo "Cancelled."
        exit 0
    fi
    echo ""
fi

# Installation steps
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Installation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${CYAN}[1/9]${NC} Installing system packages..."
if [[ "$OS" =~ ^(ubuntu|debian)$ ]]; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq >/dev/null 2>&1
    apt-get install -y -qq python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx >/dev/null 2>&1
elif [[ "$OS" =~ ^(centos|rhel|rocky|almalinux)$ ]]; then
    yum install -y -q python3 python3-pip git nginx certbot python3-certbot-nginx >/dev/null 2>&1
fi
echo -e "${GREEN}✓ Packages installed${NC}"

echo -e "${CYAN}[2/9]${NC} Creating directory..."
mkdir -p "$INSTALL_DIR" && cd "$INSTALL_DIR"
echo -e "${GREEN}✓ Directory: ${INSTALL_DIR}${NC}"

echo -e "${CYAN}[3/9]${NC} Downloading source..."
if [ -d "$INSTALL_DIR/.git" ]; then
    git pull -q origin main 2>/dev/null || true
else
    git clone -q "$REPO_URL" "$INSTALL_DIR" 2>/dev/null
fi
echo -e "${GREEN}✓ Source ready${NC}"

echo -e "${CYAN}[4/9]${NC} Creating Python environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓ Virtualenv created${NC}"

echo -e "${CYAN}[5/9]${NC} Installing Python packages..."
pip install -q --upgrade pip setuptools wheel
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Packages installed${NC}"

echo -e "${CYAN}[6/9]${NC} Setting up CLI..."
ln -sf "$INSTALL_DIR/cli/starlyproxy-cli.py" /usr/local/bin/starlyproxy
chmod +x "$INSTALL_DIR/cli/starlyproxy-cli.py"
echo -e "${GREEN}✓ CLI: starlyproxy${NC}"

echo -e "${CYAN}[7/9]${NC} Initializing database..."
python3 -c "import sys; sys.path.insert(0, '$INSTALL_DIR'); from core import DatabaseManager; DatabaseManager()"
echo -e "${GREEN}✓ Database ready${NC}"

cat > "$INSTALL_DIR/panel_config.json" << EOF
{
    "domain": "${PANEL_DOMAIN}",
    "port": ${PANEL_PORT},
    "ssl_enabled": ${ENABLE_SSL}
}
EOF

echo -e "${CYAN}[8/9]${NC} Configuring web server..."
if [ ! -z "$PANEL_DOMAIN" ]; then
    cat > /etc/nginx/conf.d/starlyproxy.conf << 'NGEOF'
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;
    location / {
        proxy_pass http://127.0.0.1:PORT_PLACEHOLDER;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
NGEOF
    sed -i "s/DOMAIN_PLACEHOLDER/${PANEL_DOMAIN}/g" /etc/nginx/conf.d/starlyproxy.conf
    sed -i "s/PORT_PLACEHOLDER/${PANEL_PORT}/g" /etc/nginx/conf.d/starlyproxy.conf
    
    nginx -t >/dev/null 2>&1 && systemctl restart nginx >/dev/null 2>&1
    echo -e "${GREEN}✓ Nginx configured${NC}"
    
    if [ "$ENABLE_SSL" = true ] && command -v certbot >/dev/null; then
        echo -e "${CYAN}   Obtaining SSL certificate...${NC}"
        certbot --nginx -d "${PANEL_DOMAIN}" --non-interactive --agree-tos --register-unsafely-without-email --redirect >/dev/null 2>&1
        [ $? -eq 0 ] && echo -e "${GREEN}✓ SSL configured${NC}" || echo -e "${YELLOW}⚠ SSL failed${NC}"
    fi
else
    echo -e "${GREEN}✓ IP-only mode${NC}"
fi

echo -e "${CYAN}[9/9]${NC} Creating service..."
cat > /etc/systemd/system/starlyproxy-panel.service << EOF
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
EOF

systemctl daemon-reload
systemctl enable starlyproxy-panel >/dev/null 2>&1
echo -e "${GREEN}✓ Service created${NC}"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   ✅ Installation Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Start Panel:${NC}"
echo -e "  systemctl start starlyproxy-panel"
echo ""
echo -e "${CYAN}Access:${NC}"
if [ ! -z "$PANEL_DOMAIN" ]; then
    [ "$ENABLE_SSL" = true ] && echo -e "  ${GREEN}https://${PANEL_DOMAIN}${NC}" || echo -e "  ${GREEN}http://${PANEL_DOMAIN}${NC}"
else
    IP=$(hostname -I | awk '{print $1}')
    [ ! -z "$IP" ] && echo -e "  ${GREEN}http://${IP}:${PANEL_PORT}${NC}" || echo -e "  ${GREEN}http://YOUR_IP:${PANEL_PORT}${NC}"
fi
echo ""
echo -e "${YELLOW}CLI Usage:${NC}"
echo -e "  starlyproxy list"
echo -e "  starlyproxy add myproxy paqet client IP:PORT \"Key\""
echo -e "  starlyproxy start myproxy"
echo ""
echo -e "${BLUE}🎉 Done!${NC}"
echo ""
