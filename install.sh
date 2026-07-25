#!/bin/bash
#
# StarlyProxy Installer Script
# نصب و راه‌اندازی اولیه StarlyProxy v3.0
#

set -e

INSTALL_DIR="/opt/starlyproxy"
REPO_URL="https://github.com/arimakomi/StarlyProxy.git"
VENV_DIR="$INSTALL_DIR/venv"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo -e "${RED}❌ این اسکریپت باید با دسترسی root اجرا شود${NC}"
    exit 1
fi

echo -e "${GREEN}✓ دسترسی root تایید شد${NC}"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo -e "${RED}❌ سیستم عامل شناسایی نشد${NC}"
    exit 1
fi

echo -e "${GREEN}✓ سیستم عامل: $OS $VER${NC}"

# Install system dependencies
echo -e "\n${BLUE}📦 نصب وابستگی‌های سیستمی...${NC}"

if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
    apt-get update -qq
    apt-get install -y python3 python3-pip python3-venv git libpcap-dev \
        build-essential python3-dev >/dev/null 2>&1
elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]] || [[ "$OS" == "rocky" ]]; then
    yum install -y python3 python3-pip python3-devel git libpcap-devel \
        gcc gcc-c++ make >/dev/null 2>&1
else
    echo -e "${YELLOW}⚠️  سیستم عامل شناخته شده نیست. ممکن است نیاز به نصب دستی وابستگی‌ها باشد.${NC}"
fi

echo -e "${GREEN}✓ وابستگی‌های سیستمی نصب شدند${NC}"

# Create installation directory
echo -e "\n${BLUE}📁 ایجاد دایرکتوری نصب...${NC}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Clone or update repository
if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "${BLUE}🔄 بروزرسانی از مخزن...${NC}"
    git pull origin main
else
    echo -e "${BLUE}📥 دانلود از مخزن...${NC}"
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

echo -e "${GREEN}✓ کد منبع آماده شد${NC}"

# Create virtual environment
echo -e "\n${BLUE}🐍 ایجاد محیط مجازی Python...${NC}"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo -e "${GREEN}✓ محیط مجازی ایجاد شد${NC}"

# Install Python dependencies
echo -e "\n${BLUE}📦 نصب وابستگی‌های Python...${NC}"
pip install --upgrade pip setuptools wheel >/dev/null 2>&1
pip install -r requirements.txt >/dev/null 2>&1

echo -e "${GREEN}✓ وابستگی‌های Python نصب شدند${NC}"

# Create symlink for CLI
echo -e "\n${BLUE}🔗 ایجاد لینک CLI...${NC}"
ln -sf "$INSTALL_DIR/cli/starlyproxy-cli.py" /usr/local/bin/starlyproxy
chmod +x "$INSTALL_DIR/cli/starlyproxy-cli.py"

echo -e "${GREEN}✓ CLI در دسترس است: starlyproxy${NC}"

# Initialize database
echo -e "\n${BLUE}💾 مقداردهی اولیه دیتابیس...${NC}"
python3 << EOF
import sys
sys.path.insert(0, '$INSTALL_DIR')
from core import DatabaseManager
db = DatabaseManager()
print("Database initialized")
EOF

echo -e "${GREEN}✓ دیتابیس آماده شد${NC}"

# Create systemd service for web panel
echo -e "\n${BLUE}🌐 ایجاد سرویس پنل وب...${NC}"

cat > /etc/systemd/system/starlyproxy-panel.service << EOF
[Unit]
Description=StarlyProxy Web Panel
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR/panel
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable starlyproxy-panel.service

echo -e "${GREEN}✓ سرویس پنل وب ایجاد شد${NC}"

# Final message
echo -e "\n${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ نصب StarlyProxy با موفقیت کامل شد!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📍 مسیر نصب:${NC} $INSTALL_DIR"
echo ""
echo -e "${YELLOW}🚀 راه‌اندازی سریع:${NC}"
echo -e "   1. شروع پنل وب: ${GREEN}systemctl start starlyproxy-panel${NC}"
echo -e "   2. دسترسی به پنل: ${GREEN}http://YOUR_SERVER_IP:5000${NC}"
echo -e "   3. استفاده از CLI: ${GREEN}starlyproxy list${NC}"
echo ""
echo -e "${YELLOW}📖 دستورات CLI:${NC}"
echo -e "   ${GREEN}starlyproxy list${NC}              - لیست instance ها"
echo -e "   ${GREEN}starlyproxy add${NC}               - افزودن instance جدید"
echo -e "   ${GREEN}starlyproxy start <name>${NC}     - شروع instance"
echo -e "   ${GREEN}starlyproxy stop <name>${NC}      - توقف instance"
echo -e "   ${GREEN}starlyproxy status <name>${NC}    - نمایش وضعیت"
echo -e "   ${GREEN}starlyproxy logs <name>${NC}      - نمایش لاگ‌ها"
echo ""
echo -e "${YELLOW}🌐 پنل وب:${NC}"
echo -e "   ${GREEN}systemctl start starlyproxy-panel${NC}   - شروع پنل"
echo -e "   ${GREEN}systemctl status starlyproxy-panel${NC}  - وضعیت پنل"
echo -e "   ${GREEN}systemctl enable starlyproxy-panel${NC}  - فعال‌سازی خودکار"
echo ""
echo -e "${BLUE}🎉 از StarlyProxy استفاده کنید!${NC}"
echo ""
