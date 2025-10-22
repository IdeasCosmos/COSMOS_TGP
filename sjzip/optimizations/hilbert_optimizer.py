"""Hilbert Curve 3D optimization with security."""

import numpy as np
from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class HilbertPoint:
    """Point on Hilbert curve (immutable)."""
    index: int
    x: int
    y: int
    z: int
    normalized_coords: Tuple[float, float, float]

    def __post_init__(self):
        """Validate point data."""
        if self.index < 0:
            raise ValueError(f"Invalid index: {self.index}")
        if any(c < 0 for c in [self.x, self.y, self.z]):
            raise ValueError("Coordinates must be non-negative")


class HilbertCurve3D:
    """Secure 3D Hilbert Curve implementation."""

    MAX_ORDER = 10  # Prevent excessive memory usage

    def __init__(self, order: int = 8):
        if not (1 <= order <= self.MAX_ORDER):
            raise ValueError(f"Order must be between 1 and {self.MAX_ORDER}")
        
        self.order = order
        self.max_coord = 2 ** order - 1
        self.total_points = 2 ** (3 * order)

    def hilbert_index_to_3d(self, index: int) -> Tuple[int, int, int]:
        """Convert 1D Hilbert index to 3D coordinates with validation."""
        if not (0 <= index < self.total_points):
            raise ValueError(f"Index {index} out of range [0, {self.total_points})")
        
        x = y = z = 0
        
        for level in range(self.order):
            n = 2 ** (self.order - level - 1)
            octant = (index // (n * n * n)) % 8
            
            if octant & 1:
                x += n
            if octant & 2:
                y += n
            if octant & 4:
                z += n
        
        return x, y, z

    def coords_3d_to_hilbert_index(self, x: int, y: int, z: int) -> int:
        """Convert 3D coordinates to Hilbert index with validation."""
        if not all(0 <= c <= self.max_coord for c in [x, y, z]):
            raise ValueError(f"Coordinates out of range [0, {self.max_coord}]")
        
        index = 0
        
        for level in range(self.order):
            n = 2 ** (self.order - level - 1)
            octant = 0
            
            if x >= n:
                octant |= 1
                x -= n
            if y >= n:
                octant |= 2
                y -= n
            if z >= n:
                octant |= 4
                z -= n
            
            index += octant * (n * n * n)
        
        return index

    def compress_with_hilbert(self, coordinates: np.ndarray) -> bytes:
        """Compress 4D coordinates using Hilbert curve."""
        if not isinstance(coordinates, np.ndarray) or coordinates.shape != (4,):
            raise ValueError("Coordinates must be numpy array of shape (4,)")
        
        scaled_coords = (coordinates[:3] * self.max_coord).astype(np.int32)
        scaled_coords = np.clip(scaled_coords, 0, self.max_coord)
        
        hilbert_idx = self.coords_3d_to_hilbert_index(
            int(scaled_coords[0]),
            int(scaled_coords[1]),
            int(scaled_coords[2])
        )
        
        time_encoded = int(np.clip(coordinates[3], 0, 1) * 65535)
        
        return hilbert_idx.to_bytes(3, 'big') + time_encoded.to_bytes(2, 'big')

    def decompress_from_hilbert(self, compressed: bytes) -> np.ndarray:
        """Decompress coordinates from Hilbert encoding."""
        if len(compressed) != 5:
            raise ValueError(f"Expected 5 bytes, got {len(compressed)}")
        
        hilbert_idx = int.from_bytes(compressed[:3], 'big')
        time_encoded = int.from_bytes(compressed[3:5], 'big')
        
        if hilbert_idx >= self.total_points:
            raise ValueError(f"Invalid Hilbert index: {hilbert_idx}")
        
        x, y, z = self.hilbert_index_to_3d(hilbert_idx)
        
        coords = np.array([
            x / self.max_coord,
            y / self.max_coord,
            z / self.max_coord,
            time_encoded / 65535.0
        ], dtype=np.float64)
        
        return coords
