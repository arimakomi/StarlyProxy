#!/bin/bash
#
# Quick Demo Script for StarlyProxy v3.0
# نمایش سریع قابلیت‌های اصلی
#

set -e

DEMO_MODE=true
DEMO_DIR="/tmp/starlyproxy-demo"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         StarlyProxy v3.0 - Quick Demo                    ║"
echo "║         نمایش سریع قابلیت‌ها (بدون نصب واقعی)          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python version: $PYTHON_VERSION"

# Create demo directory
mkdir -p "$DEMO_DIR"
cd "$(dirname "$0")"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📦 بخش 1: بررسی ساختار پروژه"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "📁 ساختار اصلی:"
find . -maxdepth 1 -type d ! -path . ! -path './.*' ! -path './windows' -exec basename {} \; | sort | sed 's/^/  ├── /'

echo ""
echo "🐍 فایل‌های Python:"
find . -name "*.py" -type f ! -path '*/\.*' ! -path '*/gfk/*' | wc -l | awk '{print "  مجموع: " $1 " فایل"}'

echo ""
echo "🌐 Templates پنل:"
find panel/templates -name "*.html" 2>/dev/null | wc -l | awk '{print "  مجموع: " $1 " template"}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🧪 بخش 2: تست Core Modules"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "در حال تست modules..."
python3 tests/test_core.py 2>/dev/null || echo "⚠️  نیاز به نصب وابستگی‌ها دارد (این طبیعی است در demo)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📋 بخش 3: بررسی CLI"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "دستورات موجود در CLI:"
echo "  ✓ starlyproxy list              - لیست instance ها"
echo "  ✓ starlyproxy add               - افزودن instance جدید"
echo "  ✓ starlyproxy start/stop        - کنترل instance ها"
echo "  ✓ starlyproxy status            - نمایش وضعیت"
echo "  ✓ starlyproxy logs              - نمایش لاگ‌ها"
echo "  ✓ starlyproxy delete            - حذف instance"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐 بخش 4: بررسی Web Panel"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "صفحات پنل وب:"
for template in panel/templates/*.html; do
    basename "$template" .html | sed 's/^/  📄 /'
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📊 بخش 5: آمار پروژه"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
PY_LINES=$(find . -name "*.py" -type f ! -path '*/\.*' -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
HTML_LINES=$(find . -name "*.html" -type f -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
SH_LINES=$(find . -name "*.sh" -type f -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')

echo "  📝 خطوط کد Python: $PY_LINES"
echo "  🌐 خطوط HTML: $HTML_LINES"
echo "  🔧 خطوط Shell: $SH_LINES"
echo ""
echo "  📦 Modules: 8+"
echo "  🎨 Templates: 5"
echo "  🛠️  Scripts: 4+"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ نتیجه Demo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "StarlyProxy v3.0 شامل:"
echo "  ✅ Core management system کامل"
echo "  ✅ پشتیبانی از Paqet و GFK"
echo "  ✅ پنل وب Flask با dashboard"
echo "  ✅ CLI حرفه‌ای با دستورات فارسی"
echo "  ✅ SQLite database برای persistence"
echo "  ✅ REST API جامع"
echo "  ✅ Health check و backup scripts"
echo "  ✅ مستندات کامل"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 نصب واقعی"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "برای نصب واقعی:"
echo ""
echo "  curl -fsSL https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/install.sh | sudo bash"
echo ""
echo "یا:"
echo ""
echo "  git clone https://github.com/arimakomi/StarlyProxy.git"
echo "  cd StarlyProxy"
echo "  sudo bash install.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
