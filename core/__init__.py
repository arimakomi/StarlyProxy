"""
StarlyProxy Core Module
Central management for multi-instance proxy system
"""

__version__ = "3.0.0"
__author__ = "STaRly (Artin)"

from .config import ConfigManager
from .database import DatabaseManager
from .instance_manager import InstanceManager
from .utils import (
    detect_network_interface,
    get_local_ip,
    get_gateway_mac,
    find_free_port,
    validate_ip,
    validate_port
)

__all__ = [
    'ConfigManager',
    'DatabaseManager', 
    'InstanceManager',
    'detect_network_interface',
    'get_local_ip',
    'get_gateway_mac',
    'find_free_port',
    'validate_ip',
    'validate_port'
]
