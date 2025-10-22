"""
SJZIP - Secure Text Compression System
=======================================

A secure, optimized text compression codec using 3D spiral space mapping.

Version: 2.0.0
Security Level: High
"""

__version__ = "2.0.0"
__author__ = "Multibus TGP Team"
__license__ = "MIT"

# Security configuration
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB limit
MAX_CHUNK_SIZE = 500
ALLOWED_EXTENSIONS = {'.txt', '.sjz', '.sjzo'}

from .alphabet import ALPHABET, ALPHABET_SIZE
from .codec import SJZIPCodec, DotRecord, CHUNK_SIZE
from .dot import DotCodec, DotPacket, SingleDot

__all__ = [
    'ALPHABET',
    'ALPHABET_SIZE',
    'SJZIPCodec',
    'DotRecord',
    'DotCodec',
    'DotPacket',
    'SingleDot',
    'CHUNK_SIZE',
]
