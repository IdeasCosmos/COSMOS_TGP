"""Front-specific ordering and timing rules for SJZIP with security."""

from __future__ import annotations

from typing import Dict, List
import logging

from .alphabet import ALPHABET, ensure_supported
from .mapper import SpiralSpaceMapperExtended

# Configure logging
logger = logging.getLogger(__name__)

# Initialize mapper securely
_mapper = SpiralSpaceMapperExtended()

# Immutable lookups (computed once)
_FRONT_ORDERS: Dict[str, tuple] = {}
_FRONT_POSITIONS: Dict[str, Dict[str, int]] = {}

# Build front orders with security
for front in ALPHABET:
    order: List[str] = []
    if front not in order:
        order.append(front)
    if front != 'A' and 'A' not in order:
        order.append('A')
    for char in ALPHABET:
        if char in order:
            continue
        order.append(char)

    # Store as immutable tuple
    _FRONT_ORDERS[front] = tuple(order)
    _FRONT_POSITIONS[front] = {char: idx for idx, char in enumerate(order)}


def front_order(front: str) -> tuple:
    """
    Get front-specific character ordering.

    Args:
        front: Front character

    Returns:
        Immutable tuple of characters in front-specific order

    Raises:
        ValueError: If front character is not supported
    """
    ensure_supported(front)

    try:
        return _FRONT_ORDERS[front]
    except KeyError as exc:
        raise ValueError(f"No front order for character {front!r}") from exc


def front_position(front: str, char: str) -> int:
    """
    Get position of character in front-specific ordering.

    Args:
        front: Front character
        char: Character to find position for

    Returns:
        Zero-based position index

    Raises:
        ValueError: If character is not supported in the front
    """
    ensure_supported(front)
    ensure_supported(char)

    try:
        return _FRONT_POSITIONS[front][char]
    except KeyError as exc:
        raise ValueError(
            f"Character {char!r} not found in front {front!r} ordering"
        ) from exc


# Time lookup (computed once, immutable)
_TIME_LOOKUP: Dict[str, float] = {}
for row in _mapper.character_map.itertuples():
    angle = (row.angle_deg % 360.0) / 360.0
    _TIME_LOOKUP[row.char] = angle


def char_time_fraction(char: str) -> float:
    """
    Get time fraction [0, 1] for character.

    Args:
        char: Character to get time fraction for

    Returns:
        Time fraction in [0, 1] range

    Raises:
        ValueError: If character is not supported
    """
    ensure_supported(char)

    try:
        return _TIME_LOOKUP[char]
    except KeyError as exc:
        raise ValueError(f"No time fraction for character {char!r}") from exc
