"""Quaternion rotation optimization with security."""

import numpy as np
from typing import Tuple
from dataclasses import dataclass
import struct


@dataclass
class Quaternion:
    """Unit quaternion (immutable)."""
    w: float
    x: float
    y: float
    z: float

    def __post_init__(self):
        """Validate quaternion."""
        if not all(isinstance(v, (int, float)) for v in [self.w, self.x, self.y, self.z]):
            raise TypeError("Quaternion components must be numeric")

    def normalize(self) -> 'Quaternion':
        """Return normalized quaternion."""
        norm = np.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
        if norm < 1e-10:
            return Quaternion(1, 0, 0, 0)
        return Quaternion(
            self.w / norm,
            self.x / norm,
            self.y / norm,
            self.z / norm
        )


class QuaternionSpiralEncoder:
    """Secure quaternion-based spiral encoding."""

    MAX_ROTATIONS = 5.0

    def __init__(self, max_rotations: float = 5.0):
        if not (0 < max_rotations <= 100):
            raise ValueError("max_rotations must be in (0, 100]")
        
        self.max_rotations = max_rotations
        self.max_angle = max_rotations * 2 * np.pi
        self.precision_bits = 16
        self.max_value = 2 ** self.precision_bits - 1

    def angle_radius_to_quaternion(self, angle_rad: float, radius: float, depth: float = 0.0) -> Quaternion:
        """Convert spiral parameters to quaternion with validation."""
        if not all(isinstance(v, (int, float)) for v in [angle_rad, radius, depth]):
            raise TypeError("Parameters must be numeric")
        
        radius = np.clip(radius, 0, 1)
        depth = np.clip(depth, 0, 1)
        
        half_angle = angle_rad / 2
        
        w = np.cos(half_angle)
        x = radius * np.cos(angle_rad) * 0.1
        y = radius * np.sin(angle_rad) * 0.1
        z = np.sin(half_angle) + depth * 0.1
        
        return Quaternion(w, x, y, z).normalize()

    def quaternion_to_angle_radius(self, quat: Quaternion) -> Tuple[float, float, float]:
        """Restore spiral parameters from quaternion."""
        quat = quat.normalize()
        
        half_angle = np.arctan2(quat.z, quat.w)
        angle_rad = 2 * half_angle
        
        radius_x = quat.x / 0.1
        radius_y = quat.y / 0.1
        radius = np.sqrt(radius_x**2 + radius_y**2)
        
        depth = (quat.z - np.sin(half_angle)) / 0.1
        
        return angle_rad, max(0, min(1, radius)), max(0, min(1, depth))

    def compress_quaternion(self, quat: Quaternion) -> bytes:
        """Compress quaternion to 6 bytes."""
        quat = quat.normalize()
        
        x_scaled = int(np.clip((quat.x + 1.0) * 0.5 * self.max_value, 0, self.max_value))
        y_scaled = int(np.clip((quat.y + 1.0) * 0.5 * self.max_value, 0, self.max_value))
        z_scaled = int(np.clip((quat.z + 1.0) * 0.5 * self.max_value, 0, self.max_value))
        
        return struct.pack('>HHH', x_scaled, y_scaled, z_scaled)

    def decompress_quaternion(self, compressed: bytes) -> Quaternion:
        """Decompress quaternion from 6 bytes."""
        if len(compressed) != 6:
            raise ValueError(f"Expected 6 bytes, got {len(compressed)}")
        
        x_scaled, y_scaled, z_scaled = struct.unpack('>HHH', compressed)
        
        x = (x_scaled / self.max_value) * 2.0 - 1.0
        y = (y_scaled / self.max_value) * 2.0 - 1.0
        z = (z_scaled / self.max_value) * 2.0 - 1.0
        
        w_squared = 1.0 - (x**2 + y**2 + z**2)
        
        if w_squared < 0:
            norm = np.sqrt(x**2 + y**2 + z**2)
            if norm > 0:
                x /= norm
                y /= norm
                z /= norm
            w = 0.0
        else:
            w = np.sqrt(w_squared)
        
        return Quaternion(w, x, y, z)


class QuaternionOptimizedMapper:
    """Quaternion-optimized character mapper."""

    def __init__(self, max_rotations: float = 5.0):
        self.encoder = QuaternionSpiralEncoder(max_rotations)
        self._quat_cache = {}

    def compress_character_position(self, char: str) -> bytes:
        """Compress character to position bytes."""
        if not isinstance(char, str) or len(char) != 1:
            raise ValueError("Expected single character")
        
        char_index = ord(char) - 32 if 32 <= ord(char) <= 126 else 0
        char_index = min(max(0, char_index), 96)
        
        t = char_index / 96
        angle_rad = t * self.encoder.max_angle
        radius = 0.01 + t * 0.49
        depth = t
        
        quat = self.encoder.angle_radius_to_quaternion(angle_rad, radius, depth)
        return self.encoder.compress_quaternion(quat)
