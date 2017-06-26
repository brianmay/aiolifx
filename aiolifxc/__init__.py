"""Top-level package for aiolifxc."""

from .aiolifx import LifxDiscovery
from .message import *
from .msgtypes import *
from .unpack import unpack_lifx_message

__author__ = """Brian May"""
__email__ = 'brian@linuxpenguins.xyz'
__version__ = '0.5.1'
