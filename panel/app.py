#!/usr/bin/env python3
"""
StarlyProxy Web Panel
Professional web-based management interface
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import sys
import os
from pathlib import Path
import json

# Fix import path
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ['PYTHONPATH'] = str(PROJECT_ROOT)

try:
    from core import InstanceManager, ConfigManager, DatabaseManager
    from core.utils import format_bytes, format_duration, get_system_info
except ImportError as e:
    print(f"CRITICAL: Cannot import core modules: {e}")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"sys.path: {sys.path}")
    sys.exit(1)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'starlyproxy-secret-key-change-in-production'
CORS(app)

mgr = InstanceManager()
config_mgr = ConfigManager()
db_mgr = DatabaseManager()


@app.route('/')
def index():
    """Dashboard main page"""
    instances = mgr.list_instances()
    
    total = len(instances)
    running = sum(1 for i in instances if i.get('status') == 'running')
    stopped = total - running
    
    system_info = get_system_info()
    
    return render_template('dashboard.html',
                          instances=instances,
                          total=total,
                          running=running,
                          stopped=stopped,
                          system_info=system_info)


@app.route('/instances')
def instances_page():
    """Instances list page"""
    instances = []
    for name in config_mgr.list_instances():
        status = mgr.get_instance_status(name)
        if status:
            instances.append(status)
    
    return render_template('instances.html', instances=instances)


@app.route('/add')
def add_page():
    """Add new instance page"""
    return render_template('add.html')


@app.route('/settings')
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
    return render_template('settings.html', config=config, system_info=system_info)


@app.route('/api/instances', methods=['GET'])
def api_list_instances():
    """API: List all instances"""
    instances = mgr.list_instances()
    return jsonify({'success': True, 'instances': instances})


@app.route('/api/instances/add', methods=['POST'])
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
def api_start_instance(name):
    """API: Start instance"""
    success = mgr.start_instance(name)
    return jsonify({'success': success})


@app.route('/api/instances/<name>/stop', methods=['POST'])
def api_stop_instance(name):
    """API: Stop instance"""
    success = mgr.stop_instance(name)
    return jsonify({'success': success})


@app.route('/api/instances/<name>/restart', methods=['POST'])
def api_restart_instance(name):
    """API: Restart instance"""
    success = mgr.restart_instance(name)
    return jsonify({'success': success})


@app.route('/api/instances/<name>/delete', methods=['DELETE'])
def api_delete_instance(name):
    """API: Delete instance"""
    success = mgr.delete_instance(name)
    return jsonify({'success': success})


@app.route('/api/instances/<name>/status', methods=['GET'])
def api_get_status(name):
    """API: Get instance status"""
    status = mgr.get_instance_status(name)
    if status:
        return jsonify({'success': True, 'status': status})
    else:
        return jsonify({'success': False, 'error': 'Instance not found'}), 404


@app.route('/api/instances/<name>/logs', methods=['GET'])
def api_get_logs(name):
    """API: Get instance logs"""
    lines = request.args.get('lines', 100, type=int)
    logs = mgr.get_instance_logs(name, lines=lines)
    return jsonify({'success': True, 'logs': logs})


@app.route('/api/instances/stop-all', methods=['POST'])
def api_stop_all():
    """API: Stop all instances"""
    instances = mgr.list_instances()
    stopped = 0
    for inst in instances:
        if mgr.stop_instance(inst['name']):
            stopped += 1
    return jsonify({'success': True, 'stopped': stopped})


@app.route('/api/instances/start-all', methods=['POST'])
def api_start_all():
    """API: Start all instances"""
    instances = mgr.list_instances()
    started = 0
    for inst in instances:
        if mgr.start_instance(inst['name']):
            started += 1
    return jsonify({'success': True, 'started': started})


@app.route('/api/system', methods=['GET'])
def api_system_info():
    """API: Get system information"""
    info = get_system_info()
    return jsonify({'success': True, 'system': info})


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting StarlyProxy Web Panel on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug)
