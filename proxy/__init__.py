"""
Proxy module for StarlyProxy
Contains wrappers for different proxy types
"""

from .paqet_wrapper import PaqetWrapper
from .gfk_wrapper import GFKWrapper

__all__ = ['PaqetWrapper', 'GFKWrapper']
