"""
StarlyProxy Web Panel - Flask Application
پنل مدیریت وب با dashboard کامل
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import InstanceManager, ConfigManager, DatabaseManager
from core.utils import format_bytes, format_duration, get_system_info

app = Flask(__name__)
app.config['SECRET_KEY'] = 'starlyproxy-secret-key-change-me'

mgr = InstanceManager()
config_mgr = ConfigManager()
db_mgr = DatabaseManager()


@app.route('/')
def index():
    """Dashboard صفحه اصلی"""
    instances = mgr.list_instances()
    
    # محاسبه آمار کلی
    total = len(instances)
    running = sum(1 for i in instances if i['status'] == 'running')
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
    """صفحه لیست instance ها"""
    instances = []
    for name in config_mgr.list_instances():
        status = mgr.get_instance_status(name)
        if status:
            instances.append(status)
    
    return render_template('instances.html', instances=instances)


@app.route('/instance/<name>')
def instance_detail(name):
    """صفحه جزئیات instance"""
    status = mgr.get_instance_status(name)
    if not status:
        return "Instance not found", 404
    
    # دریافت لاگ‌ها
    logs = db_mgr.get_logs(instance_name=name, limit=100)
    
    # دریافت آمار
    stats = db_mgr.get_stats(name, hours=24)
    
    return render_template('instance_detail.html',
                          instance=status,
                          logs=logs,
                          stats=stats)


@app.route('/add', methods=['GET', 'POST'])
def add_instance():
    """صفحه افزودن instance جدید"""
    if request.method == 'POST':
        name = request.form.get('name')
        instance_type = request.form.get('type')
        mode = request.form.get('mode')
        server = request.form.get('server')
        key = request.form.get('key')
        profile = request.form.get('profile', 'standard')
        
        # Parse server address
        if ':' in server:
            server_ip, server_port = server.rsplit(':', 1)
            server_port = int(server_port)
        else:
            return jsonify({'error': 'فرمت آدرس سرور نادرست است'}), 400
        
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
            return redirect(url_for('instances_page'))
        else:
            return jsonify({'error': 'خطا در ایجاد instance'}), 500
    
    return render_template('add_instance.html')


@app.route('/api/instance/<name>/start', methods=['POST'])
def api_start_instance(name):
    """API: شروع instance"""
    if mgr.start_instance(name):
        return jsonify({'success': True, 'message': f'Instance {name} started'})
    return jsonify({'success': False, 'error': 'Failed to start instance'}), 500


@app.route('/api/instance/<name>/stop', methods=['POST'])
def api_stop_instance(name):
    """API: توقف instance"""
    force = request.json.get('force', False) if request.is_json else False
    if mgr.stop_instance(name, force=force):
        return jsonify({'success': True, 'message': f'Instance {name} stopped'})
    return jsonify({'success': False, 'error': 'Failed to stop instance'}), 500


@app.route('/api/instance/<name>/restart', methods=['POST'])
def api_restart_instance(name):
    """API: ریستارت instance"""
    if mgr.restart_instance(name):
        return jsonify({'success': True, 'message': f'Instance {name} restarted'})
    return jsonify({'success': False, 'error': 'Failed to restart instance'}), 500


@app.route('/api/instance/<name>/delete', methods=['DELETE'])
def api_delete_instance(name):
    """API: حذف instance"""
    if mgr.delete_instance(name, stop_first=True):
        return jsonify({'success': True, 'message': f'Instance {name} deleted'})
    return jsonify({'success': False, 'error': 'Failed to delete instance'}), 500


@app.route('/api/instance/<name>/status')
def api_instance_status(name):
    """API: دریافت وضعیت instance"""
    status = mgr.get_instance_status(name)
    if status:
        return jsonify(status)
    return jsonify({'error': 'Instance not found'}), 404


@app.route('/api/instances')
def api_list_instances():
    """API: لیست همه instance ها"""
    instances = mgr.list_instances()
    return jsonify(instances)


@app.route('/api/stats/<name>')
def api_instance_stats(name):
    """API: آمار instance"""
    hours = request.args.get('hours', 24, type=int)
    stats = db_mgr.get_stats(name, hours=hours)
    return jsonify(stats)


@app.route('/api/logs/<name>')
def api_instance_logs(name):
    """API: لاگ‌های instance"""
    limit = request.args.get('limit', 100, type=int)
    logs = db_mgr.get_logs(instance_name=name, limit=limit)
    return jsonify(logs)


@app.route('/api/system')
def api_system_info():
    """API: اطلاعات سیستم"""
    return jsonify(get_system_info())


@app.template_filter('format_bytes')
def format_bytes_filter(value):
    """Template filter: فرمت بایت"""
    return format_bytes(value)


@app.template_filter('format_duration')
def format_duration_filter(value):
    """Template filter: فرمت مدت زمان"""
    return format_duration(value)


@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')


@app.route('/api/instances/stop-all', methods=['POST'])
def api_stop_all():
    """Stop all instances"""
    try:
        mgr = InstanceManager()
        instances = mgr.list_instances()
        stopped = 0
        
        for inst in instances:
            if inst.get('status') == 'running':
                if mgr.stop_instance(inst['name']):
                    stopped += 1
        
        return jsonify({'success': True, 'stopped': stopped})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/system')
def api_system():
    """System information"""
    try:
        import psutil
        
        return jsonify({
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
