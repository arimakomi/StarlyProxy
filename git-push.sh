#!/bin/bash
#
# Git push script for StarlyProxy v3.0
# آماده‌سازی و push به GitHub
#

set -e

cd "$(dirname "$0")"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         StarlyProxy v3.0 - Git Push                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in a git repo
if [ ! -d .git ]; then
    echo "❌ Not a git repository. Initializing..."
    git init
    git remote add origin https://github.com/arimakomi/StarlyProxy.git
fi

echo "📋 آماده‌سازی فایل‌ها..."

# Add all files
git add .

echo ""
echo "📊 تغییرات:"
git status --short

echo ""
read -p "آیا می‌خواهید commit کنید؟ (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "لغو شد."
    exit 0
fi

echo ""
echo "📝 Commit message:"
cat << 'EOF'

feat: StarlyProxy v3.0 - Complete Rewrite

🎉 Major Release: Complete rewrite with professional architecture

✨ New Features:
- Multi-instance management with unlimited simultaneous instances
- Beautiful Flask web panel with live dashboard
- Powerful Persian CLI with comprehensive commands
- SQLite database for persistence and stats
- Full REST API for automation
- Integrated Paqet and GFK support
- Auto-restart and health monitoring
- Comprehensive logging and statistics

🏗️ Architecture:
- Core management system (ConfigManager, DatabaseManager, InstanceManager)
- Proxy wrappers for Paqet and GFK
- Modular and extensible design
- Proper error handling and logging

📚 Documentation:
- Complete README with examples
- API documentation
- Troubleshooting guide
- Contributing guidelines
- Changelog and summary

🛠️ Tools:
- install.sh - One-command installation
- health_check.sh - Automatic health monitoring
- backup.sh - Config and database backup
- demo.sh - Quick demo without installation

📊 Stats:
- ~4,500 lines of Python code
- 725 lines of HTML templates
- 8+ core modules
- 5 web templates
- Full systemd integration

Breaking Changes:
- Complete file structure change
- New CLI commands (starlyproxy instead of paqctl)
- Old configs not compatible

Migration:
Users should reinstall and recreate instances with the new system.

Co-authored-by: STaRly (Artin) <artin@starly.me>
EOF

git commit -m "feat: StarlyProxy v3.0 - Complete Rewrite" \
    -m "Major rewrite with multi-instance management, web panel, and professional architecture" \
    -m "" \
    -m "See CHANGELOG.md for full details"

echo ""
echo "✅ Committed successfully"
echo ""
read -p "آیا می‌خواهید به GitHub push کنید؟ (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "برای push دستی:"
    echo "  git push origin main"
    exit 0
fi

echo ""
echo "🚀 Pushing to GitHub..."
git push origin main --force-with-lease

echo ""
echo "✅ Push completed!"
echo ""
echo "🎉 StarlyProxy v3.0 is now live on GitHub!"
