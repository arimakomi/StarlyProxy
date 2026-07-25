#!/usr/bin/env python3
"""
Quick test script for StarlyProxy core functionality
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("StarlyProxy v3.0 - Quick Test")
print("=" * 60)

# Test imports
print("\n[1/5] Testing imports...")
try:
    from core import ConfigManager, DatabaseManager, InstanceManager
    from core.utils import detect_network_interface, get_local_ip
    print("✅ Core imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test config manager
print("\n[2/5] Testing ConfigManager...")
try:
    config_mgr = ConfigManager(config_dir="/tmp/test_starlyproxy")
    setting = config_mgr.get_setting('base_socks_port', 1080)
    print(f"✅ ConfigManager OK (base_socks_port: {setting})")
except Exception as e:
    print(f"❌ ConfigManager failed: {e}")
    sys.exit(1)

# Test database manager
print("\n[3/5] Testing DatabaseManager...")
try:
    db_mgr = DatabaseManager(db_path="/tmp/test_starlyproxy.db")
    print("✅ DatabaseManager OK")
    db_mgr.close()
except Exception as e:
    print(f"❌ DatabaseManager failed: {e}")
    sys.exit(1)

# Test network detection
print("\n[4/5] Testing network detection...")
try:
    interface = detect_network_interface()
    local_ip = get_local_ip(interface)
    print(f"✅ Network detection OK")
    print(f"   Interface: {interface}")
    print(f"   Local IP: {local_ip}")
except Exception as e:
    print(f"⚠️  Network detection warning: {e}")
    print("   (This is OK if running in container)")

# Test instance manager initialization
print("\n[5/5] Testing InstanceManager...")
try:
    # Note: This will use /tmp paths from config above
    inst_mgr = InstanceManager()
    print("✅ InstanceManager OK")
except Exception as e:
    print(f"❌ InstanceManager failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All core tests passed!")
print("=" * 60)
print("\nNext steps:")
print("  1. Install: sudo bash install.sh")
print("  2. Start panel: sudo systemctl start starlyproxy-panel")
print("  3. Add instance: sudo starlyproxy add ...")
print("=" * 60)
