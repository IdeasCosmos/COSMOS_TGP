"""Spiral space mapper with extended alphabet support and security validations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import numpy as np
import pandas as pd

from .alphabet import ALPHABET, ALPHABET_SIZE, CHAR_TO_INDEX, ensure_supported


@dataclass(frozen=True)
class SpiralProperties:
    """Precomputed spatial properties for a character (immutable for security)."""

    char: str
    index: int
    angle_deg: float
    angle_rad: float
    radius: float
    depth: float
    time: float
    distance: float
    x: float
    y: float
    z: float
    t: float

    def __post_init__(self):
        """Validate properties after initialization."""
        # Validate numeric ranges
        if not (0 <= self.index < ALPHABET_SIZE):
            raise ValueError(f"Invalid index: {self.index}")
        if not (0 <= self.radius <= 1):
            raise ValueError(f"Invalid radius: {self.radius}")
        if not (0 <= self.depth <= 1):
            raise ValueError(f"Invalid depth: {self.depth}")
        if not all(0 <= coord <= 1 for coord in [self.x, self.y, self.z]):
            raise ValueError("Coordinates must be in [0, 1] range")


class SpiralSpaceMapperExtended:
    """Maps characters to coordinates in the conical spiral space with security."""

    # Constants (immutable)
    MAX_ROTATIONS = 5.0
    INITIAL_RADIUS = 0.01
    FINAL_RADIUS = 0.5
    MAX_DEPTH = 1.0
    FRONT_CENTER = np.array([0.5, 0.5, 0.5, 0.0])

    def __init__(self) -> None:
        """Initialize mapper with precomputed secure mappings."""
        self.character_map = self._generate_character_mapping()
        self._property_cache: Dict[str, SpiralProperties] = {
            row.char: SpiralProperties(
                char=row.char,
                index=row.index,
                angle_deg=row.angle_deg,
                angle_rad=row.angle_rad,
                radius=row.radius,
                depth=row.depth,
                time=row.time,
                distance=row.distance,
                x=row.x,
                y=row.y,
                z=row.z,
                t=row.t,
            )
            for row in self.character_map.itertuples()
        }
        # Make cache read-only-like by not providing setter methods

    def _generate_character_mapping(self) -> pd.DataFrame:
        """Generate secure character mappings with validation."""
        total_chars = ALPHABET_SIZE
        characters = ALPHABET
        total_angle = self.MAX_ROTATIONS * 2 * np.pi
        mappings = []

        for idx, char in enumerate(characters):
            # Secure division handling
            t_param = idx / max(1, total_chars - 1)

            angle_rad = t_param * total_angle
            angle_deg = np.degrees(angle_rad)
            radius = self.INITIAL_RADIUS + t_param * (self.FINAL_RADIUS - self.INITIAL_RADIUS)
            depth = t_param * self.MAX_DEPTH
            time_coord = depth

            if idx == 0:
                distance = 0.0
            else:
                dr = (self.FINAL_RADIUS - self.INITIAL_RADIUS) / max(1, total_chars - 1)
                dtheta = total_angle / max(1, total_chars - 1)
                dz = self.MAX_DEPTH / max(1, total_chars - 1)
                r_prev = self.INITIAL_RADIUS + ((idx - 1) / max(1, total_chars - 1)) * (
                    self.FINAL_RADIUS - self.INITIAL_RADIUS
                )
                ds = np.sqrt(dr**2 + (r_prev * dtheta)**2 + dz**2)
                distance = ds * idx

            x_offset = radius * np.cos(angle_rad)
            y_offset = radius * np.sin(angle_rad)

            # Secure coordinate clamping
            x = np.clip(self.FRONT_CENTER[0] + x_offset, 0.0, 1.0)
            y = np.clip(self.FRONT_CENTER[1] + y_offset, 0.0, 1.0)
            z = np.clip(self.FRONT_CENTER[2] - depth, 0.0, 1.0)
            t = np.clip(time_coord, 0.0, 1.0)

            mappings.append({
                "char": char,
                "ascii": ord(char),
                "index": idx,
                "angle_deg": angle_deg,
                "angle_rad": angle_rad,
                "radius": radius,
                "depth": depth,
                "time": time_coord,
                "distance": distance,
                "x": x,
                "y": y,
                "z": z,
                "t": t,
            })

        return pd.DataFrame(mappings)

    def get_properties(self, char: str) -> SpiralProperties:
        """
        Get spatial properties for a character with security validation.

        Args:
            char: Single character

        Returns:
            Immutable SpiralProperties object

        Raises:
            ValueError: If character is not supported
            TypeError: If input is not a string
        """
        ensure_supported(char)

        try:
            return self._property_cache[char]
        except KeyError as exc:
            raise ValueError(f"Character {char!r} not in property cache") from exc

    def get_index(self, char: str) -> int:
        """Get alphabet index for character with validation."""
        ensure_supported(char)
        return CHAR_TO_INDEX[char]

    def get_front_id(self, char: str) -> int:
        """Get front ID for character (alias for get_index)."""
        return self.get_index(char)
