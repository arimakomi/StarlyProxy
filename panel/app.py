#!/usr/bin/env python3
"""
StarlyProxy Enhanced Web Panel
Professional web-based management interface with authentication
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_cors import CORS
from functools import wraps
import sys
import os
import subprocess
from pathlib import Path
import json

# Fix import path
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ['PYTHONPATH'] = str(PROJECT_ROOT)

try:
    from core import InstanceManager, ConfigManager
    from core.auth import AuthManager
    from core.backup import BackupManager
    from core.metrics import MetricsCollector
    from core.multiserver import MultiServerManager
    from core.xray import XrayManager, InboundManager, OutboundManager, UserManager
    from core.utils import get_system_info
except ImportError as e:
    print(f"CRITICAL: Cannot import core modules: {e}")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    sys.exit(1)

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'starlyproxy-change-in-production')
CORS(app)

# Initialize managers
mgr = InstanceManager()
config_mgr = ConfigManager()
auth_mgr = AuthManager()
backup_mgr = BackupManager()
metrics_mgr = MetricsCollector()
multiserver_mgr = MultiServerManager()
xray_mgr = XrayManager()
xray_inbound_mgr = InboundManager()
xray_outbound_mgr = OutboundManager()
xray_user_mgr = UserManager()


# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


# Import and register Xray routes
from xray_routes import register_xray_routes
register_xray_routes(app, xray_mgr, xray_inbound_mgr, xray_outbound_mgr, xray_user_mgr, login_required)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if auth_mgr.verify_password(username, password):
            token = auth_mgr.create_session(username)
            session['auth_token'] = token
            session['username'] = username
            session['user_id'] = username  # Required by login_required decorator
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    token = session.get('auth_token')
    if token:
        auth_mgr.logout(token)
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """Dashboard main page"""
    instances = mgr.list_instances()
    
    total = len(instances)
    running = sum(1 for i in instances if i.get('status') == 'running')
    stopped = total - running
    
    system_info = get_system_info()
    
    return render_template('dashboard_v3.html',
                          instances=instances,
                          total=total,
                          running=running,
                          stopped=stopped,
                          system_info=system_info,
                          username=session.get('username'))


@app.route('/instances')
@login_required
def instances_page():
    """Instances list page"""
    instances = []
    for name in config_mgr.list_instances():
        status = mgr.get_instance_status(name)
        if status:
            instances.append(status)
    return render_template('instances.html', instances=instances)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_page():
    """Add new instance page"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            instance_type = request.form.get('type', 'paqet')
            mode = request.form.get('mode', 'client')
            server = request.form.get('server', '').strip()
            key = request.form.get('key', '').strip()
            port = request.form.get('port', '').strip()
            
            if not all([name, server, key, port]):
                flash('All fields are required!', 'danger')
                return redirect('/add')
            
            result = mgr.create_instance(
                name=name,
                instance_type=instance_type,
                mode=mode,
                server_address=server.split(':')[0],
                server_port=int(server.split(':')[1]) if ':' in server else 8443,
                secret_key=key,
                local_port=int(port)
            )
            
            if result:
                flash(f'Instance {name} created successfully!', 'success')
                return redirect('/instances')
            else:
                flash('Error creating instance', 'danger')
                return redirect('/add')
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect('/add')
    
    return render_template('add.html')


@app.route('/settings')
@login_required
def settings_page():
    """Settings page"""
    config = {}
    try:
        config_file = PROJECT_ROOT / 'panel_config.json'
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
    except:
        pass
    
    system_info = get_system_info()
    return render_template('settings_v3.html', config=config, system_info=system_info)


@app.route('/backups')
@login_required
def backups_page():
    """Backup management page"""
    backups = backup_mgr.list_backups()
    return render_template('backups_v3.html', backups=backups)


@app.route('/metrics')
@login_required
def metrics_page():
    """Metrics and monitoring page"""
    system_metrics = metrics_mgr.collect_system_metrics()
    return render_template('metrics_v3.html', metrics=system_metrics)


@app.route('/servers')
@login_required
def servers_page():
    """Multi-server management page"""
    servers = multiserver_mgr.list_servers()
    return render_template('servers_v3.html', servers=servers)


@app.route('/users')
@login_required
def users_page():
    """User management page (admin only)"""
    return render_template('users_v3.html')


# Xray Routes
@app.route('/xray')
@login_required
def xray_dashboard():
    """Xray dashboard page"""
    return render_template('xray_dashboard.html')


@app.route('/xray/inbounds')
@login_required
def xray_inbounds_page():
    """Xray inbounds page"""
    return render_template('xray_inbounds.html')


@app.route('/xray/outbounds')
@login_required
def xray_outbounds_page():
    """Xray outbounds page"""
    return render_template('xray_outbounds.html')


@app.route('/xray/users')
@login_required
def xray_users_page():
    """Xray users page"""
    return render_template('xray_users.html')


# API Routes
@app.route('/api/instances', methods=['GET'])
@login_required
def api_list_instances():
    """API: List all instances"""
    instances = mgr.list_instances()
    return jsonify({'success': True, 'instances': instances})


@app.route('/api/instances/add', methods=['POST'])
@login_required
def api_add_instance():
    """API: Add new instance"""
    data = request.get_json()
    
    name = data.get('name')
    instance_type = data.get('type', 'paqet')
    mode = data.get('mode', 'client')
    server = data.get('server')
    key = data.get('key')
    profile = data.get('profile', 'default')
    
    if not all([name, server, key]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    if ':' in server:
        server_ip, server_port = server.rsplit(':', 1)
        server_port = int(server_port)
    else:
        return jsonify({'success': False, 'error': 'Invalid server format'}), 400
    
    success = mgr.create_instance(
        name=name,
        instance_type=instance_type,
        mode=mode,
        server_address=server_ip,
        server_port=server_port,
        secret_key=key,
        profile=profile
    )
    
    if success:
        return jsonify({'success': True, 'message': 'Instance created'})
    else:
        return jsonify({'success': False, 'error': 'Failed to create instance'}), 500


@app.route('/api/instances/<name>/start', methods=['POST'])
@login_required
def api_start_instance(name):
    """API: Start instance"""
    success = mgr.start_instance(name)
    return jsonify({'success': success})


@app.route('/api/instances/<name>/stop', methods=['POST'])
@login_required
def api_stop_instance(name):
    """API: Stop instance"""
    success = mgr.stop_instance(name)
    return jsonify({'success': success})


@app.route('/api/instances/<name>/restart', methods=['POST'])
@login_required
def api_restart_instance(name):
    """API: Restart instance"""
    success = mgr.restart_instance(name)
    return jsonify({'success': success})


@app.route('/api/instances/<name>/delete', methods=['DELETE'])
@login_required
def api_delete_instance(name):
    """API: Delete instance"""
    success = mgr.delete_instance(name)
    return jsonify({'success': success})


@app.route('/api/instances/<name>/status', methods=['GET'])
@login_required
def api_get_status(name):
    """API: Get instance status"""
    status = mgr.get_instance_status(name)
    if status:
        return jsonify({'success': True, 'status': status})
    else:
        return jsonify({'success': False, 'error': 'Instance not found'}), 404


@app.route('/api/instances/<name>/logs', methods=['GET'])
@login_required
def api_get_logs(name):
    """API: Get instance logs"""
    lines = request.args.get('lines', 100, type=int)
    logs = mgr.get_instance_logs(name, lines=lines)
    return jsonify({'success': True, 'logs': logs})


@app.route('/api/instances/stop-all', methods=['POST'])
@login_required
def api_stop_all():
    """API: Stop all instances"""
    instances = mgr.list_instances()
    stopped = 0
    for inst in instances:
        if mgr.stop_instance(inst['name']):
            stopped += 1
    return jsonify({'success': True, 'stopped': stopped})


@app.route('/api/instances/start-all', methods=['POST'])
@login_required
def api_start_all():
    """API: Start all instances"""
    instances = mgr.list_instances()
    started = 0
    for inst in instances:
        if mgr.start_instance(inst['name']):
            started += 1
    return jsonify({'success': True, 'started': started})


# Backup API Routes
@app.route('/api/backups/create', methods=['POST'])
@login_required
def api_create_backup():
    """API: Create backup"""
    data = request.get_json() or {}
    name = data.get('name')
    
    backup_path = backup_mgr.create_backup(name)
    return jsonify({'success': True, 'backup': backup_path})


@app.route('/api/backups/list', methods=['GET'])
@login_required
def api_list_backups():
    """API: List backups"""
    backups = backup_mgr.list_backups()
    return jsonify({'success': True, 'backups': backups})


@app.route('/api/backups/restore', methods=['POST'])
@login_required
def api_restore_backup():
    """API: Restore backup"""
    data = request.get_json()
    name = data.get('name')
    
    success = backup_mgr.restore_backup(name)
    return jsonify({'success': success})


@app.route('/api/backups/delete/<name>', methods=['DELETE'])
@login_required
def api_delete_backup(name):
    """API: Delete backup"""
    success = backup_mgr.delete_backup(name)
    return jsonify({'success': success})


# Multi-Server API Routes
@app.route('/api/servers/add', methods=['POST'])
@login_required
def api_add_server():
    """API: Add remote server"""
    data = request.get_json()
    name = data.get('name')
    host = data.get('host')
    port = data.get('port', 5000)
    
    success = multiserver_mgr.add_server(name, host, port)
    return jsonify({'success': success})


@app.route('/api/servers/list', methods=['GET'])
@login_required
def api_list_servers():
    """API: List all servers"""
    servers = multiserver_mgr.list_servers()
    return jsonify({'success': True, 'servers': servers})


@app.route('/api/servers/<name>/status', methods=['GET'])
@login_required
def api_server_status(name):
    """API: Check server status"""
    health = multiserver_mgr.check_server_health(name)
    return jsonify({'success': True, 'health': health})


# User Management API Routes
@app.route('/api/users/add', methods=['POST'])
@login_required
def api_add_user():
    """API: Add new user"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    
    success = auth_mgr.add_user(username, password, role)
    return jsonify({'success': success})


@app.route('/api/users/list', methods=['GET'])
@login_required
def api_list_users():
    """API: List users"""
    users = auth_mgr.list_users()
    return jsonify({'success': True, 'users': users})


@app.route('/api/metrics/system', methods=['GET'])
@login_required
def api_system_metrics():
    """API: Get system metrics"""
    metrics = metrics_mgr.collect_system_metrics()
    return jsonify({'success': True, 'metrics': metrics})


@app.route('/api/system/check-updates', methods=['GET'])
@login_required
def api_check_updates():
    """API: Check for updates via git"""
    try:
        subprocess.run(
            ['git', 'fetch', 'origin', 'main'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            timeout=30
        )

        current = subprocess.run(
            ['git', 'describe', '--tags', '--always'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        ).stdout.strip()

        latest = subprocess.run(
            ['git', 'describe', '--tags', '--always', 'origin/main'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        ).stdout.strip()

        status = subprocess.run(
            ['git', 'status', '-uno'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        ).stdout

        update_available = current != latest or 'Your branch is behind' in status

        return jsonify({
            'success': True,
            'current_version': current,
            'latest_version': latest,
            'update_available': update_available
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/system/update', methods=['POST'])
@login_required
def api_system_update():
    """API: Perform system update via git pull and restart the panel service"""
    try:
        result = subprocess.run(
            ['git', 'pull', 'origin', 'main'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            return jsonify({'success': False, 'error': result.stderr.strip()}), 500

        # Restart the panel service in the background so this request can
        # still return a response to the client first.
        subprocess.Popen(
            ['systemctl', 'restart', 'starlyproxy-panel'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return jsonify({'success': True, 'message': 'Update applied, panel is restarting'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    print(f"Starting StarlyProxy Enhanced Web Panel on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug)
