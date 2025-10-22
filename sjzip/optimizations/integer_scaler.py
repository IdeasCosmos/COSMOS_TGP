"""Integer Coordinate Scaling with security validation."""

import struct
import numpy as np
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class ScalingConfig:
    """Coordinate scaling configuration (immutable)."""
    x_bits: int = 16
    y_bits: int = 16
    z_bits: int = 16
    t_bits: int = 12
    x_range: Tuple[float, float] = (0.0, 1.0)
    y_range: Tuple[float, float] = (0.0, 1.0)
    z_range: Tuple[float, float] = (0.0, 1.0)
    t_range: Tuple[float, float] = (0.0, 1.0)

    def __post_init__(self):
        """Validate configuration."""
        if not all(1 <= b <= 32 for b in [self.x_bits, self.y_bits, self.z_bits, self.t_bits]):
            raise ValueError("Bit sizes must be between 1 and 32")
        for r in [self.x_range, self.y_range, self.z_range, self.t_range]:
            if r[0] >= r[1]:
                raise ValueError(f"Invalid range: {r}")


class IntegerCoordinateScaler:
    """Secure integer coordinate scaling."""

    MAX_COORDS = 10000  # Prevent memory exhaustion

    def __init__(self, config: Optional[ScalingConfig] = None):
        self.config = config or ScalingConfig()
        self.x_max = 2 ** self.config.x_bits - 1
        self.y_max = 2 ** self.config.y_bits - 1
        self.z_max = 2 ** self.config.z_bits - 1
        self.t_max = 2 ** self.config.t_bits - 1
        self._compute_scale_factors()

    def _compute_scale_factors(self):
        """Calculate scaling factors."""
        self.x_scale = self.x_max / (self.config.x_range[1] - self.config.x_range[0])
        self.y_scale = self.y_max / (self.config.y_range[1] - self.config.y_range[0])
        self.z_scale = self.z_max / (self.config.z_range[1] - self.config.z_range[0])
        self.t_scale = self.t_max / (self.config.t_range[1] - self.config.t_range[0])

    def scale_to_integer(self, coords: np.ndarray) -> Tuple[int, int, int, int]:
        """Scale float coordinates to integers with validation."""
        if not isinstance(coords, np.ndarray) or coords.shape != (4,):
            raise ValueError("Coordinates must be numpy array of shape (4,)")
        
        x = np.clip(coords[0], *self.config.x_range)
        y = np.clip(coords[1], *self.config.y_range)
        z = np.clip(coords[2], *self.config.z_range)
        t = np.clip(coords[3], *self.config.t_range)
        
        x_int = min(int((x - self.config.x_range[0]) * self.x_scale), self.x_max)
        y_int = min(int((y - self.config.y_range[0]) * self.y_scale), self.y_max)
        z_int = min(int((z - self.config.z_range[0]) * self.z_scale), self.z_max)
        t_int = min(int((t - self.config.t_range[0]) * self.t_scale), self.t_max)
        
        return x_int, y_int, z_int, t_int

    def scale_from_integer(self, x_int: int, y_int: int, z_int: int, t_int: int) -> np.ndarray:
        """Restore float coordinates from integers."""
        x = (x_int / self.x_scale) + self.config.x_range[0]
        y = (y_int / self.y_scale) + self.config.y_range[0]
        z = (z_int / self.z_scale) + self.config.z_range[0]
        t = (t_int / self.t_scale) + self.config.t_range[0]
        return np.array([x, y, z, t], dtype=np.float64)

    def pack_coordinates(self, coords: np.ndarray) -> bytes:
        """Pack coordinates to 8 bytes with validation."""
        x_int, y_int, z_int, t_int = self.scale_to_integer(coords)
        
        packed = 0
        packed |= (x_int & 0xFFFF) << 44
        packed |= (y_int & 0xFFFF) << 28
        packed |= (z_int & 0xFFFF) << 12
        packed |= (t_int & 0x0FFF)
        
        return packed.to_bytes(8, byteorder='big')

    def unpack_coordinates(self, packed: bytes) -> np.ndarray:
        """Unpack coordinates from bytes with validation."""
        if len(packed) != 8:
            raise ValueError(f"Expected 8 bytes, got {len(packed)}")
        
        packed_int = int.from_bytes(packed, byteorder='big')
        
        x_int = (packed_int >> 44) & 0xFFFF
        y_int = (packed_int >> 28) & 0xFFFF
        z_int = (packed_int >> 12) & 0xFFFF
        t_int = packed_int & 0x0FFF
        
        return self.scale_from_integer(x_int, y_int, z_int, t_int)

    def pack_multiple(self, coords_list: List[np.ndarray]) -> bytes:
        """Pack multiple coordinates with security limits."""
        if len(coords_list) > self.MAX_COORDS:
            raise ValueError(f"Too many coordinates: {len(coords_list)} > {self.MAX_COORDS}")
        
        packed_data = bytearray()
        packed_data.extend(struct.pack('>I', len(coords_list)))
        
        for coords in coords_list:
            packed_data.extend(self.pack_coordinates(coords))
        
        return bytes(packed_data)

    def unpack_multiple(self, packed: bytes) -> List[np.ndarray]:
        """Unpack multiple coordinates with validation."""
        if len(packed) < 4:
            raise ValueError("Insufficient data for count")
        
        count = struct.unpack('>I', packed[:4])[0]
        
        if count > self.MAX_COORDS:
            raise ValueError(f"Too many coordinates: {count} > {self.MAX_COORDS}")
        
        expected_size = 4 + count * 8
        if len(packed) != expected_size:
            raise ValueError(f"Size mismatch: expected {expected_size}, got {len(packed)}")
        
        offset = 4
        coords_list = []
        
        for _ in range(count):
            coord_bytes = packed[offset:offset+8]
            coords = self.unpack_coordinates(coord_bytes)
            coords_list.append(coords)
            offset += 8
        
        return coords_list
