"""
GFK (GFW-Knocker) Wrapper for StarlyProxy
Manages GFK client/server instances with proper lifecycle
"""

import subprocess
import sys
import os
import json
import signal
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger("StarlyProxy.GFK")


class GFKWrapper:
    """Wrapper for GFW-Knocker proxy instances"""
    
    def __init__(self, instance_config: Dict[str, Any]):
        self.config = instance_config
        self.name = instance_config['name']
        self.mode = instance_config['mode']
        self.base_dir = Path("/opt/starlyproxy")
        self.gfk_dir = self.base_dir / "proxy" / "gfk"
        self.instance_dir = self.base_dir / "instances" / self.name
        self.instance_dir.mkdir(parents=True, exist_ok=True)
        
        self.process = None
    
    def _create_parameters_file(self) -> Path:
        """Create parameters.py for this instance"""
        params_file = self.instance_dir / "parameters.py"
        
        params_content = f'''"""
Auto-generated parameters for {self.name}
"""

# Server configuration
vps_ip = "{self.config['server_address']}"

# Ports
vio_tcp_server_port = {self.config.get('vio_tcp_port', 8443)}
vio_udp_server_port = {self.config.get('vio_tcp_port', 8443) + 1}
quic_server_port = {self.config.get('quic_port', 14000)}

'''
        
        if self.mode == 'client':
            params_content += f'''
# Client-specific
vio_tcp_client_port = {self.config.get('vio_tcp_port', 8443) + 100}
vio_udp_client_port = {self.config.get('vio_tcp_port', 8443) + 101}
quic_client_port = {self.config.get('quic_port', 14000) + 100}
quic_local_ip = "127.0.0.1"
socks_port = {self.config['socks_port']}

# Network configuration
my_ip = "{self.config.get('local_ip', '192.168.1.100')}"
gateway_mac = "{self.config.get('gateway_mac', 'aa:bb:cc:dd:ee:ff')}"
interface = "{self.config.get('interface', 'eth0')}"
'''
        
        params_content += f'''
# Protocol settings
tcp_flags = "{self.config.get('tcp_flags', 'AP')}"
udp_timeout = 120

# Security
encryption_key = "{self.config['secret_key']}"
'''
        
        with open(params_file, 'w') as f:
            f.write(params_content)
        
        logger.info(f"Created parameters file: {params_file}")
        return params_file
    
    def start(self) -> Optional[int]:
        """Start GFK instance"""
        try:
            # Create parameters file
            self._create_parameters_file()
            
            # Determine which script to run
            if self.mode == 'client':
                script_dir = self.gfk_dir / "client"
                main_script = script_dir / "mainclient.py"
            else:
                script_dir = self.gfk_dir / "server"
                main_script = script_dir / "mainserver.py"
            
            if not main_script.exists():
                logger.error(f"GFK script not found: {main_script}")
                return None
            
            # Set up environment
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.instance_dir) + ":" + str(self.gfk_dir)
            
            # Start process
            log_file = self.instance_dir / "gfk.log"
            log_handle = open(log_file, 'a')
            
            self.process = subprocess.Popen(
                [sys.executable, str(main_script)],
                cwd=str(script_dir),
                env=env,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid  # Create new process group
            )
            
            logger.info(f"Started GFK {self.mode} for {self.name}, PID: {self.process.pid}")
            return self.process.pid
            
        except Exception as e:
            logger.error(f"Failed to start GFK instance: {e}", exc_info=True)
            return None
    
    def stop(self, force: bool = False) -> bool:
        """Stop GFK instance"""
        try:
            if self.process:
                if force:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                else:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                
                logger.info(f"Stopped GFK instance {self.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to stop GFK instance: {e}", exc_info=True)
            return False
    
    @staticmethod
    def get_default_ports(base_port: int = 14000) -> Dict[str, int]:
        """Get default port configuration for GFK"""
        return {
            'quic_port': base_port,
            'vio_tcp_port': 8443,
        }
