#!/bin/bash
#
# Backup Script for StarlyProxy
# پشتیبان‌گیری از configs و database
#

BACKUP_DIR="${BACKUP_DIR:-/root/starlyproxy-backups}"
STARLYPROXY_DIR="/opt/starlyproxy"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/starlyproxy_backup_$TIMESTAMP.tar.gz"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "📦 Creating backup of StarlyProxy..."
echo "Backup location: $BACKUP_FILE"

# Create temporary directory
TMP_DIR=$(mktemp -d)

# Copy configs
echo "📄 Backing up configurations..."
cp -r "$STARLYPROXY_DIR/instances" "$TMP_DIR/" 2>/dev/null || true
cp "$STARLYPROXY_DIR/config.json" "$TMP_DIR/" 2>/dev/null || true

# Copy database
echo "💾 Backing up database..."
cp "$STARLYPROXY_DIR/starlyproxy.db" "$TMP_DIR/" 2>/dev/null || true

# Create tarball
echo "🗜️  Compressing..."
tar -czf "$BACKUP_FILE" -C "$TMP_DIR" .

# Clean up
rm -rf "$TMP_DIR"

# Check if successful
if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✅ Backup created successfully!"
    echo "   File: $BACKUP_FILE"
    echo "   Size: $SIZE"
    
    # Keep only last 7 backups
    echo "🧹 Cleaning old backups (keeping last 7)..."
    ls -t "$BACKUP_DIR"/starlyproxy_backup_*.tar.gz | tail -n +8 | xargs -r rm -f
    
    echo "✓ Backup complete"
else
    echo "❌ Backup failed!"
    exit 1
fi
