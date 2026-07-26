"""
Xray API Routes for StarlyProxy Panel
Separate file to keep panel/app.py manageable
"""

from flask import jsonify, request


def register_xray_routes(app, xray_mgr, xray_inbound_mgr, xray_outbound_mgr, xray_user_mgr, login_required):
    """Register Xray API routes"""
    
    @app.route('/api/xray/status', methods=['GET'])
    @login_required
    def api_xray_status():
        """Get Xray service status"""
        try:
            status = xray_mgr.get_status()
            inbounds = xray_inbound_mgr.list_inbounds()
            outbounds = xray_outbound_mgr.list_outbounds()
            users = xray_user_mgr.list_users()
            
            return jsonify({
                'success': True,
                'running': status.get('running', False),
                'version': status.get('version'),
                'inbound_count': len(inbounds),
                'outbound_count': len(outbounds),
                'user_count': len(users)
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/start', methods=['POST'])
    @login_required
    def api_xray_start():
        """Start Xray service"""
        try:
            result = xray_mgr.start()
            return jsonify({'success': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/stop', methods=['POST'])
    @login_required
    def api_xray_stop():
        """Stop Xray service"""
        try:
            result = xray_mgr.stop()
            return jsonify({'success': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/restart', methods=['POST'])
    @login_required
    def api_xray_restart():
        """Restart Xray service"""
        try:
            result = xray_mgr.restart()
            return jsonify({'success': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/inbounds', methods=['GET'])
    @login_required
    def api_xray_list_inbounds():
        """List Xray inbounds"""
        try:
            inbounds = xray_inbound_mgr.list_inbounds()
            return jsonify({'success': True, 'inbounds': inbounds})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/inbounds/add', methods=['POST'])
    @login_required
    def api_xray_add_inbound():
        """Add Xray inbound"""
        try:
            data = request.get_json()
            protocol = data['protocol']
            port = data['port']
            tag = data.get('tag')
            
            # Create default client for testing
            clients = [{'id': xray_inbound_mgr.config.generate_uuid(), 'email': 'default@test'}]
            
            if protocol == 'vmess':
                result = xray_inbound_mgr.add_vmess(port, clients, tag=tag)
            elif protocol == 'vless':
                result = xray_inbound_mgr.add_vless(port, clients, tag=tag)
            elif protocol == 'trojan':
                result = xray_inbound_mgr.add_trojan(port, ['password123'], tag=tag)
            elif protocol == 'shadowsocks':
                result = xray_inbound_mgr.add_shadowsocks(port, 'password123', tag=tag)
            else:
                return jsonify({'success': False, 'error': 'Unsupported protocol'}), 400
            
            return jsonify({'success': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/inbounds/remove', methods=['DELETE'])
    @login_required
    def api_xray_remove_inbound():
        """Remove Xray inbound"""
        try:
            data = request.get_json()
            result = xray_inbound_mgr.remove_inbound(data['tag'])
            return jsonify({'success': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/outbounds', methods=['GET'])
    @login_required
    def api_xray_list_outbounds():
        """List Xray outbounds"""
        try:
            outbounds = xray_outbound_mgr.list_outbounds()
            return jsonify({'success': True, 'outbounds': outbounds})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/outbounds/connect', methods=['POST'])
    @login_required
    def api_xray_connect_server():
        """Connect to remote server"""
        try:
            data = request.get_json()
            result = xray_outbound_mgr.connect_server(
                server_address=data['server_address'],
                server_port=data['server_port'],
                protocol=data['protocol'],
                uuid=data['uuid'],
                tag=data.get('tag', 'proxy-server')
            )
            return jsonify({'success': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/outbounds/remove', methods=['DELETE'])
    @login_required
    def api_xray_remove_outbound():
        """Remove Xray outbound"""
        try:
            data = request.get_json()
            result = xray_outbound_mgr.remove_outbound(data['tag'])
            return jsonify({'success': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/users', methods=['GET'])
    @login_required
    def api_xray_list_users():
        """List Xray users"""
        try:
            users = xray_user_mgr.list_users()
            return jsonify({'success': True, 'users': users})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/users/add', methods=['POST'])
    @login_required
    def api_xray_add_user():
        """Add Xray user"""
        try:
            data = request.get_json()
            user = xray_user_mgr.create_user(
                email=data['email'],
                protocol=data['protocol'],
                inbound_tag=data['inbound_tag'],
                traffic_limit=data.get('traffic_limit', 0)
            )
            return jsonify({'success': bool(user), 'user': user})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/users/<uuid>', methods=['GET'])
    @login_required
    def api_xray_get_user(uuid):
        """Get user details"""
        try:
            user = xray_user_mgr.get_user(uuid)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Generate link
            link = xray_user_mgr.generate_vmess_link(uuid, '0.0.0.0', 443, user.get('email', ''))
            user['link'] = link
            
            return jsonify({'success': True, 'user': user})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/users/<uuid>', methods=['DELETE'])
    @login_required
    def api_xray_delete_user(uuid):
        """Delete user"""
        try:
            result = xray_user_mgr.delete_user(uuid)
            return jsonify({'success': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/users/<uuid>/enable', methods=['POST'])
    @login_required
    def api_xray_enable_user(uuid):
        """Enable user"""
        try:
            result = xray_user_mgr.enable_user(uuid)
            return jsonify({'success': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/xray/users/<uuid>/disable', methods=['POST'])
    @login_required
    def api_xray_disable_user(uuid):
        """Disable user"""
        try:
            result = xray_user_mgr.disable_user(uuid)
            return jsonify({'success': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
