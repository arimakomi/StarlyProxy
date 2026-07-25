# StarlyProxy

<div align="center">

![StarlyProxy Banner](https://img.shields.io/badge/StarlyProxy-v3.0-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.6%2B-yellow?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey?style=for-the-badge)

**Professional Multi-Instance Proxy Management System**

Advanced GFW-Knocker and Paqet proxy manager with web panel, CLI tools, and comprehensive monitoring.

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Architecture](#architecture)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
  - [Quick Install](#quick-install)
  - [Server Installation](#server-installation)
  - [Client Installation](#client-installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Web Panel](#web-panel)
  - [CLI Commands](#cli-commands)
  - [Configuration](#configuration)
- [Architecture](#architecture)
- [Server vs Client](#server-vs-client)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🌟 Overview

**StarlyProxy** is a professional-grade proxy management system designed for managing multiple proxy instances simultaneously. It supports both **Paqet** and **GFK** (GFW-Knocker) protocols with advanced features for monitoring, logging, and automation.

### Key Highlights

- 🚀 **Multi-Instance Management** - Run unlimited proxy instances concurrently
- 🎨 **Web Dashboard** - Beautiful, responsive web interface
- 🖥️ **Powerful CLI** - Complete command-line control
- 📊 **Real-time Monitoring** - Live stats and metrics
- 🔐 **SSL Support** - Automatic Let's Encrypt integration
- 🔄 **Auto-Restart** - Health checks and automatic recovery
- 📝 **Comprehensive Logging** - Track everything
- 🌐 **Nginx Integration** - Production-ready reverse proxy

---

## ✨ Features

### Core Features

#### Multi-Protocol Support
- **Paqet Proxy** - High-performance SOCKS5 proxy
- **GFK (GFW-Knocker)** - Advanced GFW circumvention
- Automatic port allocation
- Profile-based configurations

#### Management Interfaces

**Web Panel**
- Modern, responsive dashboard
- Real-time instance status
- Bulk operations (start/stop all)
- Settings management
- System resource monitoring
- Log viewer with filters

**CLI Tools**
- Complete instance lifecycle management
- Status monitoring and logs viewing
- Bulk operations
- Scriptable automation
- English output throughout

#### Monitoring & Reliability
- Health check system
- Auto-restart on failure
- Resource usage tracking
- Performance metrics
- SQLite-based logging
- Log retention policies

#### Deployment Features
- Systemd service integration
- Nginx reverse proxy configuration
- SSL/TLS with Let's Encrypt
- Domain-based access
- IP-only mode support
- Port selection (default, custom, auto-detect)

---

## 📦 Installation

### Prerequisites

- Linux server (Ubuntu, Debian, CentOS, AlmaLinux, Rocky Linux)
- Root or sudo access
- Python 3.6 or higher
- Internet connection

### Quick Install

The fastest way to install StarlyProxy:

```bash
curl -fsSL https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/install.sh | sudo bash
```

This will:
1. Install system dependencies
2. Download StarlyProxy
3. Setup Python environment
4. Configure web panel (default port: 5000)
5. Create CLI command
6. Enable systemd service

### Interactive Install

For custom configuration (domain, port, SSL):

```bash
wget https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/install.sh
sudo bash install.sh
```

You'll be prompted for:
- **Domain** (optional, for web panel access)
- **Port Configuration**:
  - Option 1: Use default port (5000)
  - Option 2: Choose custom port
  - Option 3: Auto-detect available port
- **SSL/TLS** (if domain provided)

---

## 🚀 Quick Start

### 1. Start the Web Panel

```bash
sudo systemctl start starlyproxy-panel
sudo systemctl enable starlyproxy-panel
```

### 2. Access the Panel

- **With domain**: `https://your-domain.com` (if SSL enabled) or `http://your-domain.com`
- **Without domain**: `http://YOUR_SERVER_IP:5000`

### 3. Create Your First Instance

**Via Web Panel:**
1. Navigate to "Add New" in the panel
2. Fill in the form:
   - Name: `my-proxy`
   - Type: `paqet`
   - Mode: `client`
   - Server: `1.2.3.4:8443`
   - Secret Key: `your-secret-key`
3. Click "Create"

**Via CLI:**
```bash
starlyproxy add my-proxy paqet client 1.2.3.4:8443 "your-secret-key"
starlyproxy start my-proxy
starlyproxy status my-proxy
```

### 4. Connect to Your Proxy

Once running, connect to the SOCKS5 port displayed in status:
```bash
# Example: SOCKS5 proxy on port 1080
curl --proxy socks5://127.0.0.1:1080 https://api.ipify.org
```

---

## 📖 Usage

### Web Panel

#### Dashboard
- Overview of all instances
- Running/stopped status
- System resource usage
- Quick actions (start, stop, restart)

#### Instance Management
- **Add New**: Create instances with form
- **List**: View all instances with details
- **Control**: Start, stop, restart, delete
- **Logs**: View real-time logs
- **Status**: Detailed status and metrics

#### Settings
- Panel configuration
- System information
- Backup/restore database
- Bulk operations
- About/version info

### Uninstallation

To completely remove StarlyProxy:

```bash
# Quick uninstall (piped)
curl -fsSL https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/uninstall.sh | sudo bash

# Or review first
wget https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/uninstall.sh
sudo bash uninstall.sh
```

The uninstaller removes:
- Systemd service
- Installation directory (`/opt/starlyproxy`)
- CLI command (`/usr/local/bin/starlyproxy`)
- All configurations and instances

---

## Updating

Check for updates and upgrade:

```bash
# Quick update
curl -fsSL https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/update.sh | sudo bash

# Or review first
wget https://raw.githubusercontent.com/arimakomi/StarlyProxy/main/update.sh
sudo bash update.sh
```

The updater will:
- Check current vs latest version
- Stop the service
- Pull latest changes
- Update dependencies
- Restart the service

You can also update via the web panel: **Settings → System → Check for Updates**

---

## CLI Commands

#### List Instances
```bash
starlyproxy list
```

Output:
```
Name                 Type     Mode     Status     SOCKS Port   Server
=================================================================================================
my-proxy            paqet    client   running    1080         1.2.3.4:8443
backup-proxy        gfk      client   stopped    -            5.6.7.8:443
```

#### Add Instance
```bash
starlyproxy add <name> <type> <mode> <server:port> <secret_key> [profile]
```

Examples:
```bash
# Paqet client
starlyproxy add prod-proxy paqet client 1.2.3.4:8443 "MySecretKey123"

# GFK client
starlyproxy add gfk-proxy gfk client 5.6.7.8:443 "AnotherSecret" premium

# Paqet server
starlyproxy add server1 paqet server 0.0.0.0:8443 "ServerSecret"
```

#### Start/Stop/Restart
```bash
starlyproxy start <name>
starlyproxy stop <name>
starlyproxy restart <name>
```

#### Status
```bash
starlyproxy status <name>
```

Output:
```
Instance: my-proxy
Type: paqet
Mode: client
Status: running
PID: 12345
SOCKS Port: 1080
Server: 1.2.3.4:8443
Uptime: 2h 34m
CPU: 0.5%
Memory: 45.2 MB
```

#### View Logs
```bash
starlyproxy logs <name> [--lines 100]
```

#### Delete Instance
```bash
starlyproxy delete <name>
```


### Configuration

#### Panel Configuration File

Located at `/opt/starlyproxy/panel_config.json`:

```json
{
  "domain": "your-domain.com",
  "port": 5000,
  "ssl_enabled": true,
  "installed_at": "2026-07-25T12:00:00Z"
}
```

#### Instance Configuration

Stored in SQLite database at `/opt/starlyproxy/instances.db`

View with:
```bash
sqlite3 /opt/starlyproxy/instances.db "SELECT * FROM instances;"
```

---

## 🏗️ Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────┐
│                    StarlyProxy System                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────┐    ┌──────────────┐    ┌────────────┐    │
│  │ Web Panel  │    │  CLI Tools   │    │  Systemd   │    │
│  │ (Flask)    │    │  (Python)    │    │  Service   │    │
│  └─────┬──────┘    └──────┬───────┘    └─────┬──────┘    │
│        │                  │                   │          │
│        └──────────────────┼───────────────────┘          │
│                           │                              │
│                   ┌───────▼────────┐                     │
│                   │ Core Modules   │                     │
│                   ├────────────────┤                     │
│                   │ InstanceManager│                     │
│                   │ ConfigManager  │                     │
│                   │ DatabaseManager│                     │
│                   └───────┬────────┘                     │
│                           │                              │
│        ┌──────────────────┼──────────────────┐           │
│        │                  │                  │           │
│   ┌────▼─────┐      ┌────▼─────┐     ┌─────▼────┐        │
│   │  Paqet   │      │   GFK    │     │ Database │        │
│   │ Instances│      │ Instances│     │ (SQLite) │        │
│   └──────────┘      └──────────┘     └──────────┘        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Directory Structure

```
/opt/starlyproxy/
├── cli/
│   └── starlyproxy-cli.py      # CLI application
├── core/
│   ├── __init__.py              # Core module exports
│   ├── instance_manager.py     # Instance lifecycle
│   ├── config.py                # Configuration management
│   ├── database.py              # Database operations
│   ├── runner.py                # Process runner
│   └── utils.py                 # Utility functions
├── panel/
│   ├── app.py                   # Flask application
│   ├── templates/               # HTML templates
│   │   ├── dashboard.html
│   │   ├── instances.html
│   │   ├── settings.html
│   │   └── base.html
│   └── static/                  # CSS, JS, images
├── proxy/
│   ├── paqet/                   # Paqet proxy binaries
│   └── gfk/                     # GFK proxy components
├── venv/                        # Python virtual environment
├── instances.db                 # SQLite database
├── panel_config.json            # Panel configuration
└── starlyproxy-wrapper.sh       # CLI wrapper script
```

### Components

#### Core Modules

**InstanceManager**
- Create, start, stop, restart instances
- Monitor instance health
- Manage process lifecycle
- Auto-restart on failure

**ConfigManager**
- Load/save instance configurations
- Profile management
- Validation

**DatabaseManager**
- SQLite operations
- Log storage
- Metrics tracking
- Query interface

**Utils**
- Network interface detection
- Port allocation
- System information
- Format helpers

#### Web Panel (Flask)
- RESTful API endpoints
- Template rendering
- CORS support
- Real-time updates

#### CLI (Python)
- Argument parsing
- Command routing
- Output formatting
- Error handling

---

## 🔄 Server vs Client

StarlyProxy supports both **server** and **client** modes for maximum flexibility.

### Server Mode

Run StarlyProxy as a **proxy server** that clients connect to:

```bash
# Create a Paqet server instance
starlyproxy add my-server paqet server 0.0.0.0:8443 "ServerSecretKey"
starlyproxy start my-server
```

**Use Cases:**
- Host proxy service for remote clients
- Central proxy infrastructure
- Multi-user proxy sharing
- Enterprise deployment

**Features:**
- Listen on any interface
- Multiple concurrent clients
- Traffic monitoring
- Access control
- Bandwidth management

### Client Mode

Run StarlyProxy as a **proxy client** connecting to remote servers:

```bash
# Create a Paqet client instance
starlyproxy add my-client paqet client 1.2.3.4:8443 "ServerSecretKey"
starlyproxy start my-client
```

**Use Cases:**
- Connect to remote proxy servers
- Local SOCKS5 proxy
- Application-specific proxying
- Desktop/laptop usage

**Features:**
- Local SOCKS5 server
- Auto-reconnect
- Connection pooling
- Failover support
- Port forwarding

### Deployment Scenarios

#### Scenario 1: Personal VPS
```
You (Client) → Internet → Your VPS (Server)
```
- Install StarlyProxy on VPS in **server mode**
- Install on local machine in **client mode**
- Connect client to server

#### Scenario 2: Multiple Servers
```
You (Client) → Server 1 (Primary)
            → Server 2 (Backup)
            → Server 3 (Fallback)
```
- Multiple server instances
- Client-side load balancing
- Automatic failover

#### Scenario 3: Team Deployment
```
Team Member 1 (Client) ┐
Team Member 2 (Client) ├→ Central Server (Server Mode)
Team Member 3 (Client) ┘
```
- Single server for team
- Centralized management
- Usage tracking per client

---

## 🔌 API Reference

### REST API Endpoints

Base URL: `http://your-server:5000/api`

#### Instance Management

**List All Instances**
```http
GET /api/instances
```

Response:
```json
{
  "success": true,
  "instances": [
    {
      "name": "my-proxy",
      "type": "paqet",
      "mode": "client",
      "status": "running",
      "socks_port": 1080,
      "server_address": "1.2.3.4:8443"
    }
  ]
}
```

**Add New Instance**
```http
POST /api/instances/add
Content-Type: application/json

{
  "name": "new-proxy",
  "type": "paqet",
  "mode": "client",
  "server": "1.2.3.4:8443",
  "key": "SecretKey123",
  "profile": "default"
}
```

**Start Instance**
```http
POST /api/instances/<name>/start
```

**Stop Instance**
```http
POST /api/instances/<name>/stop
```

**Restart Instance**
```http
POST /api/instances/<name>/restart
```

**Delete Instance**
```http
DELETE /api/instances/<name>/delete
```

**Get Instance Status**
```http
GET /api/instances/<name>/status
```

**Get Instance Logs**
```http
GET /api/instances/<name>/logs?lines=100
```

#### Bulk Operations

**Stop All Instances**
```http
POST /api/instances/stop-all
```

**Start All Instances**
```http
POST /api/instances/start-all
```

#### System Information

**Get System Info**
```http
GET /api/system
```

Response:
```json
{
  "success": true,
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 42.8,
    "disk_percent": 65.3,
    "uptime": "5 days, 12:34:56"
  }
}
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError: No module named 'core'

**Cause:** Python path not configured correctly

**Solution:**
```bash
cd /opt/starlyproxy
source venv/bin/activate
python3 -c "import core; print('OK')"
```

If still fails:
```bash
export PYTHONPATH=/opt/starlyproxy:$PYTHONPATH
```

The wrapper script handles this automatically.

#### 2. Panel Not Accessible

**Check service status:**
```bash
systemctl status starlyproxy-panel
```

**Check logs:**
```bash
journalctl -u starlyproxy-panel -n 50
```

**Restart service:**
```bash
systemctl restart starlyproxy-panel
```

#### 3. CLI Command Not Found

**Verify symlink:**
```bash
ls -la /usr/local/bin/starlyproxy
```

**Recreate if needed:**
```bash
ln -sf /opt/starlyproxy/starlyproxy-wrapper.sh /usr/local/bin/starlyproxy
chmod +x /opt/starlyproxy/starlyproxy-wrapper.sh
```

#### 4. Instance Won't Start

**Check logs:**
```bash
starlyproxy logs <instance-name>
```

**Check port availability:**
```bash
ss -tuln | grep <port>
```

**Check permissions:**
```bash
ls -la /opt/starlyproxy/instances/
```

#### 5. Installation Failed at Step [5/9]

**View installation log:**
```bash
tail -100 /tmp/starlyproxy-install.log
```

**Common causes:**
- Network issues (retry installation)
- Missing dependencies (check log for specifics)
- Insufficient disk space

**Manual fix:**
```bash
cd /opt/starlyproxy
source venv/bin/activate
pip install --no-cache-dir netifaces psutil pyyaml flask flask-cors
```

