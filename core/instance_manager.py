"""
Instance Manager for StarlyProxy
Manages multiple proxy instances (Paqet and GFK)
"""

import time
import psutil
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from .config import ConfigManager
from .database import DatabaseManager
from .utils import find_free_port

logger = logging.getLogger("StarlyProxy.InstanceManager")


class InstanceManager:
    """Manager for proxy instances"""
    
    def __init__(self):
        self.config_mgr = ConfigManager()
        self.db_mgr = DatabaseManager()
        self.base_dir = Path("/opt/starlyproxy")
        self.instances_dir = self.base_dir / "instances"
        self.instances_dir.mkdir(parents=True, exist_ok=True)
    
    def create_instance(self, name: str, instance_type: str, mode: str,
                       server_address: str, server_port: int, 
                       secret_key: str, **kwargs) -> bool:
        """
        Create new proxy instance
        
        Args:
            name: Unique instance name
            instance_type: 'paqet' or 'gfk'
            mode: 'client' or 'server'
            server_address: Server IP address
            server_port: Server port
            secret_key: Encryption key
            **kwargs: Additional configuration options
        """
        # Check if instance already exists
        if self.config_mgr.load_instance_config(name):
            logger.error(f"Instance already exists: {name}")
            return False
        
        # Find free SOCKS port for client mode
        socks_port = None
        if mode == 'client':
            base_port = self.config_mgr.get_setting('base_socks_port', 1080)
            socks_port = find_free_port(base_port)
            if not socks_port:
                logger.error("No free SOCKS port available")
                return False
        
        # Build configuration
        config = {
            'name': name,
            'type': instance_type,
            'mode': mode,
            'server_address': server_address,
            'server_port': server_port,
            'secret_key': secret_key,
            'socks_port': socks_port,
            'created_at': time.time(),
            'auto_restart': kwargs.get('auto_restart', True),
            'profile': kwargs.get('profile', 'standard'),
        }
        
        # Add type-specific config
        if instance_type == 'paqet':
            config.update(self._build_paqet_config(mode, **kwargs))
        elif instance_type == 'gfk':
            config.update(self._build_gfk_config(mode, **kwargs))
        else:
            logger.error(f"Unknown instance type: {instance_type}")
            return False
        
        # Save configuration
        if not self.config_mgr.save_instance_config(name, config):
            return False
        
        # Add to database
        server_addr_full = f"{server_address}:{server_port}"
        if not self.db_mgr.add_instance(name, instance_type, mode, 
                                        socks_port or 0, server_addr_full, config):
            self.config_mgr.delete_instance_config(name)
            return False
        
        logger.info(f"Created instance: {name} ({instance_type}/{mode})")
        return True
    
    def _build_paqet_config(self, mode: str, **kwargs) -> Dict[str, Any]:
        """Build Paqet-specific configuration"""
        from .utils import detect_network_interface, get_local_ip, get_gateway_mac
        
        interface = kwargs.get('interface') or detect_network_interface()
        local_ip = kwargs.get('local_ip') or get_local_ip(interface)
        gateway_mac = kwargs.get('gateway_mac') or get_gateway_mac(interface)
        
        return {
            'protocol': 'kcp',
            'kcp_mode': kwargs.get('kcp_mode', 'fast'),
            'interface': interface,
            'local_ip': local_ip,
            'gateway_mac': gateway_mac,
        }
    
    def _build_gfk_config(self, mode: str, **kwargs) -> Dict[str, Any]:
        """Build GFK-specific configuration"""
        from .utils import detect_network_interface, get_local_ip, get_gateway_mac
        
        interface = kwargs.get('interface') or detect_network_interface()
        local_ip = kwargs.get('local_ip') or get_local_ip(interface)
        gateway_mac = kwargs.get('gateway_mac') or get_gateway_mac(interface)
        
        # GFK uses QUIC + violated TCP
        base_quic = self.config_mgr.get_setting('base_quic_port', 14000)
        
        return {
            'protocol': 'gfk',
            'quic_port': kwargs.get('quic_port', base_quic),
            'vio_tcp_port': kwargs.get('vio_tcp_port', 8443),
            'interface': interface,
            'local_ip': local_ip,
            'gateway_mac': gateway_mac,
            'tcp_flags': kwargs.get('tcp_flags', 'AP'),
        }
    
    def start_instance(self, name: str) -> bool:
        """Start a proxy instance"""
        config = self.config_mgr.load_instance_config(name)
        if not config:
            logger.error(f"Instance not found: {name}")
            return False
        
        # Check if already running
        instance = self.db_mgr.get_instance(name)
        if instance and instance['status'] == 'running':
            logger.warning(f"Instance already running: {name}")
            return True
        
        # Start based on type
        if config['type'] == 'paqet':
            pid = self._start_paqet(name, config)
        elif config['type'] == 'gfk':
            pid = self._start_gfk(name, config)
        else:
            logger.error(f"Unknown instance type: {config['type']}")
            return False
        
        if pid:
            self.db_mgr.update_instance_status(name, 'running', pid)
            logger.info(f"Started instance: {name} (PID: {pid})")
            return True
        
        return False
    
    def _start_paqet(self, name: str, config: Dict[str, Any]) -> Optional[int]:
        """Start Paqet instance"""
        try:
            from proxy.paqet_wrapper import PaqetWrapper
            wrapper = PaqetWrapper(config)
            pid = wrapper.start()
            return pid
        except Exception as e:
            logger.error(f"Failed to start Paqet: {e}", exc_info=True)
            return None
    
    def _start_gfk(self, name: str, config: Dict[str, Any]) -> Optional[int]:
        """Start GFK instance"""
        try:
            from proxy.gfk_wrapper import GFKWrapper
            wrapper = GFKWrapper(config)
            pid = wrapper.start()
            return pid
        except Exception as e:
            logger.error(f"Failed to start GFK: {e}", exc_info=True)
            return None
    
    def stop_instance(self, name: str, force: bool = False) -> bool:
        """Stop a proxy instance"""
        instance = self.db_mgr.get_instance(name)
        if not instance:
            logger.error(f"Instance not found: {name}")
            return False
        
        if instance['status'] != 'running':
            logger.warning(f"Instance not running: {name}")
            return True
        
        pid = instance.get('pid')
        if not pid:
            logger.error(f"No PID found for instance: {name}")
            return False
        
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
                proc.wait(timeout=10)
            
            self.db_mgr.update_instance_status(name, 'stopped', None)
            logger.info(f"Stopped instance: {name}")
            return True
        except psutil.NoSuchProcess:
            self.db_mgr.update_instance_status(name, 'stopped', None)
            return True
        except Exception as e:
            logger.error(f"Failed to stop instance: {e}")
            return False
    
    def restart_instance(self, name: str) -> bool:
        """Restart a proxy instance"""
        self.stop_instance(name)
        time.sleep(1)
        return self.start_instance(name)
    
    def delete_instance(self, name: str, stop_first: bool = True) -> bool:
        """Delete a proxy instance"""
        if stop_first:
            self.stop_instance(name, force=True)
        
        # Delete from database
        if not self.db_mgr.delete_instance(name):
            return False
        
        # Delete config
        if not self.config_mgr.delete_instance_config(name):
            return False
        
        logger.info(f"Deleted instance: {name}")
        return True
    
    def list_instances(self) -> List[Dict[str, Any]]:
        """List all instances with their status"""
        return self.db_mgr.list_instances()
    
    def get_instance_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of an instance"""
        instance = self.db_mgr.get_instance(name)
        if not instance:
            return None
        
        # Check if process is actually running
        pid = instance.get('pid')
        if pid:
            try:
                proc = psutil.Process(pid)
                instance['cpu_percent'] = proc.cpu_percent(interval=0.1)
                instance['memory_mb'] = proc.memory_info().rss / (1024 * 1024)
                instance['uptime'] = time.time() - proc.create_time()
                instance['actual_status'] = 'running'
            except psutil.NoSuchProcess:
                instance['actual_status'] = 'dead'
                self.db_mgr.update_instance_status(name, 'stopped', None)
        else:
            instance['actual_status'] = 'stopped'
        
        return instance
