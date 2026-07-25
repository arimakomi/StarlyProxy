"""
Utility functions for StarlyProxy
Network detection, validation, and helper functions
"""

import socket
import subprocess
import re
import netifaces
import ipaddress
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger("StarlyProxy.Utils")


def detect_network_interface() -> Optional[str]:
    """
    Auto-detect the primary network interface
    Returns interface name like 'eth0', 'ens5', 'wlan0'
    """
    try:
        # Get default gateway interface
        gws = netifaces.gateways()
        if 'default' in gws and netifaces.AF_INET in gws['default']:
            return gws['default'][netifaces.AF_INET][1]
        
        # Fallback: find first non-loopback interface with IPv4
        for iface in netifaces.interfaces():
            if iface == 'lo':
                continue
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                return iface
    except Exception as e:
        logger.warning(f"Failed to auto-detect interface: {e}")
    
    return None


def get_local_ip(interface: Optional[str] = None) -> Optional[str]:
    """
    Get local IP address for specified interface or auto-detect
    """
    try:
        if not interface:
            interface = detect_network_interface()
        
        if interface:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                return addrs[netifaces.AF_INET][0]['addr']
        
        # Fallback: connect to external IP to find local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        logger.warning(f"Failed to get local IP: {e}")
        return None


def get_gateway_mac(interface: Optional[str] = None) -> Optional[str]:
    """
    Get gateway MAC address for specified interface
    """
    try:
        # Get gateway IP
        gws = netifaces.gateways()
        if 'default' not in gws or netifaces.AF_INET not in gws['default']:
            return None
        
        gateway_ip = gws['default'][netifaces.AF_INET][0]
        
        # Ping gateway to populate ARP table
        subprocess.run(['ping', '-c', '1', '-W', '1', gateway_ip],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)
        
        # Get MAC from ARP table
        result = subprocess.run(['ip', 'neigh', 'show', gateway_ip],
                              capture_output=True, text=True)
        
        # Parse MAC address (format: IP dev IFACE lladdr MAC_ADDR)
        match = re.search(r'lladdr\s+([0-9a-f:]{17})', result.stdout.lower())
        if match:
            return match.group(1)
        
        # Fallback: try arp command
        result = subprocess.run(['arp', '-n', gateway_ip],
                              capture_output=True, text=True)
        match = re.search(r'([0-9a-f:]{17})', result.stdout.lower())
        if match:
            return match.group(1)
            
    except Exception as e:
        logger.warning(f"Failed to get gateway MAC: {e}")
    
    return None


def find_free_port(start_port: int = 1080, max_attempts: int = 100) -> Optional[int]:
    """
    Find a free local port starting from start_port
    """
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return None


def validate_ip(ip: str) -> bool:
    """
    Validate IPv4 address
    """
    try:
        ipaddress.IPv4Address(ip)
        return True
    except (ValueError, ipaddress.AddressValueError):
        return False


def validate_port(port: int) -> bool:
    """
    Validate port number (1-65535)
    """
    return 1 <= port <= 65535


def parse_server_address(addr: str) -> Optional[Tuple[str, int]]:
    """
    Parse server address string like "1.2.3.4:8443"
    Returns (ip, port) or None if invalid
    """
    try:
        if ':' not in addr:
            return None
        ip_str, port_str = addr.rsplit(':', 1)
        port = int(port_str)
        
        if validate_ip(ip_str) and validate_port(port):
            return (ip_str, port)
    except (ValueError, AttributeError):
        pass
    
    return None


def get_system_info() -> dict:
    """
    Get system information for diagnostics
    """
    import platform
    import psutil
    
    return {
        'os': platform.system(),
        'os_version': platform.release(),
        'hostname': socket.gethostname(),
        'cpu_count': psutil.cpu_count(),
        'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
        'python_version': platform.python_version(),
    }


def check_root_privileges() -> bool:
    """
    Check if running with root/admin privileges
    """
    import os
    return os.geteuid() == 0 if hasattr(os, 'geteuid') else False


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes to human-readable string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def format_duration(seconds: float) -> str:
    """
    Format seconds to human-readable duration
    """
    seconds = int(seconds)
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return ' '.join(parts)
