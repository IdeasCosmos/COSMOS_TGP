"""Pure DOT codec for SJZIP (no filesystem side-effects) with security."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Dict, Any
import logging

from .alphabet import INDEX_TO_CHAR, validate_text, ensure_supported
from .front_space import front_order
from .codec import CHUNK_SIZE, DotRecord, SJZIPCodec

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DotPacket:
    """In-memory representation of a single DOT chunk (immutable for security)."""

    front_char: str
    front_index: int
    length: int
    x: float
    y: float
    z: float
    t: float
    payload: bytes

    def __post_init__(self):
        """Validate packet data."""
        ensure_supported(self.front_char)
        if not (0 <= self.length <= CHUNK_SIZE):
            raise ValueError(f"Invalid length: {self.length}")
        if not all(0 <= coord <= 1 for coord in [self.x, self.y, self.z, self.t]):
            raise ValueError("Coordinates must be in [0, 1] range")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary (safe for JSON serialization).

        Returns:
            Dictionary representation
        """
        return {
            "front_char": self.front_char,
            "front_index": self.front_index,
            "length": self.length,
            "coordinates": {
                "x": round(self.x, 6),  # Limit precision in output
                "y": round(self.y, 6),
                "z": round(self.z, 6),
                "t": round(self.t, 6),
            },
            "payload_hex": self.payload.hex(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DotPacket":
        """
        Create from dictionary with validation.

        Args:
            data: Dictionary containing packet data

        Returns:
            DotPacket instance

        Raises:
            ValueError: If data is invalid
            KeyError: If required fields are missing
        """
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__}")

        # Validate required fields
        required_fields = {"front_index", "length", "payload_hex"}
        missing = required_fields - data.keys()
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        coords = data.get("coordinates", {})

        # Get front_char with validation
        front_index = int(data["front_index"])
        if front_index >= len(INDEX_TO_CHAR):
            raise ValueError(f"Invalid front_index: {front_index}")

        front_char = data.get("front_char", INDEX_TO_CHAR[front_index])

        # Validate hex payload
        payload_hex = data["payload_hex"]
        if not isinstance(payload_hex, str):
            raise ValueError("payload_hex must be a string")

        try:
            payload = bytes.fromhex(payload_hex)
        except ValueError as exc:
            raise ValueError(f"Invalid hex payload: {exc}") from exc

        return DotPacket(
            front_char=front_char,
            front_index=front_index,
            length=int(data["length"]),
            x=float(coords.get("x", 0.5)),
            y=float(coords.get("y", 0.5)),
            z=float(coords.get("z", 0.5)),
            t=float(coords.get("t", 0.0)),
            payload=payload,
        )


@dataclass(frozen=True)
class SingleDot:
    """Single DOT representing entire text sequence (immutable)."""

    front_char: str
    front_index: int
    length: int
    x: float
    y: float
    z: float
    t: float
    payload: bytes

    def __post_init__(self):
        """Validate DOT data."""
        ensure_supported(self.front_char)
        if self.length <= 0:
            raise ValueError(f"Invalid length: {self.length}")
        if not all(0 <= coord <= 1 for coord in [self.x, self.y, self.z, self.t]):
            raise ValueError("Coordinates must be in [0, 1] range")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (safe for JSON)."""
        return {
            "front_char": self.front_char,
            "front_index": self.front_index,
            "length": self.length,
            "coordinates": {
                "x": round(self.x, 6),
                "y": round(self.y, 6),
                "z": round(self.z, 6),
                "t": round(self.t, 6),
            },
            "payload_hex": self.payload.hex(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SingleDot":
        """Create from dictionary with validation."""
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__}")

        required_fields = {"front_index", "length", "payload_hex"}
        missing = required_fields - data.keys()
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        coords = data.get("coordinates", {})
        front_index = int(data["front_index"])

        if front_index >= len(INDEX_TO_CHAR):
            raise ValueError(f"Invalid front_index: {front_index}")

        front_char = data.get("front_char", INDEX_TO_CHAR[front_index])

        payload_hex = data["payload_hex"]
        try:
            payload = bytes.fromhex(payload_hex)
        except ValueError as exc:
            raise ValueError(f"Invalid hex payload: {exc}") from exc

        return SingleDot(
            front_char=front_char,
            front_index=front_index,
            length=int(data["length"]),
            x=float(coords.get("x", 0.5)),
            y=float(coords.get("y", 0.5)),
            z=float(coords.get("z", 0.5)),
            t=float(coords.get("t", 0.0)),
            payload=payload,
        )


class DotCodec:
    """Expose direct text↔DOT transforms with security."""

    def __init__(self) -> None:
        """Initialize codec."""
        self._codec = SJZIPCodec()

    def text_to_dots(self, text: str) -> List[DotPacket]:
        """
        Convert text to DOT packets with validation.

        Args:
            text: Input text

        Returns:
            List of DotPacket objects

        Raises:
            ValueError: If text is invalid
        """
        if not text:
            return []

        validate_text(text)
        packets: List[DotPacket] = []

        for start in range(0, len(text), CHUNK_SIZE):
            chunk = text[start : start + CHUNK_SIZE]
            if not chunk:
                continue

            record = self._codec.encode_chunk(chunk)
            packet = DotPacket(
                front_char=chunk[0],
                front_index=record.front_index,
                length=record.length,
                x=record.x,
                y=record.y,
                z=record.z,
                t=record.t,
                payload=record.payload,
            )
            packets.append(packet)

        return packets

    def dots_to_text(self, packets: Sequence[DotPacket]) -> str:
        """
        Convert DOT packets to text with validation.

        Args:
            packets: Sequence of DotPacket objects

        Returns:
            Decoded text

        Raises:
            ValueError: If packets are invalid
        """
        if not packets:
            return ""

        text_chunks: List[str] = []

        for packet in packets:
            if packet.length > CHUNK_SIZE:
                raise ValueError(f"DOT packet length exceeds chunk size: {packet.length}")

            record = DotRecord(
                front_index=packet.front_index,
                length=packet.length,
                x=packet.x,
                y=packet.y,
                z=packet.z,
                t=packet.t,
                payload=packet.payload,
            )
            text_chunks.append(self._codec.decode_chunk(record))

        return "".join(text_chunks)

    def dots_from_dicts(self, dicts: Iterable[Dict[str, Any]]) -> List[DotPacket]:
        """
        Create DOT packets from dictionaries with validation.

        Args:
            dicts: Iterable of dictionary objects

        Returns:
            List of DotPacket objects

        Raises:
            ValueError: If data is invalid
        """
        return [DotPacket.from_dict(d) for d in dicts]

    def dots_to_dicts(self, packets: Sequence[DotPacket]) -> List[Dict[str, Any]]:
        """Convert DOT packets to dictionaries."""
        return [packet.to_dict() for packet in packets]

    def text_to_single_dot(self, text: str) -> SingleDot:
        """
        Convert entire text to single DOT with validation.

        Args:
            text: Input text

        Returns:
            SingleDot object

        Raises:
            ValueError: If text is empty or invalid
        """
        if not text:
            raise ValueError("Text must be non-empty to encode into a single DOT")

        validate_text(text)

        front_char = text[0]
        digits = self._codec._digits_from_text(front_char, text)
        payload = self._codec._payload_from_indices(digits)

        front_index = self._codec.mapper.get_front_id(front_char)
        props = self._codec.mapper.get_properties(text[-1])

        return SingleDot(
            front_char=front_char,
            front_index=front_index,
            length=len(text),
            x=props.x,
            y=props.y,
            z=props.z,
            t=props.t,
            payload=payload,
        )

    def single_dot_to_text(self, dot: SingleDot) -> str:
        """
        Convert single DOT to text with validation.

        Args:
            dot: SingleDot object

        Returns:
            Decoded text

        Raises:
            ValueError: If DOT is invalid
        """
        digits = self._codec._indices_from_payload(dot.payload, dot.length)
        order_map = front_order(dot.front_char)

        chars: List[str] = []
        for digit in digits:
            if digit >= len(order_map):
                raise ValueError(f"DOT payload decoded to unsupported digit: {digit}")
            chars.append(order_map[digit])

        return "".join(chars)

    @staticmethod
    def single_dot_to_dict(dot: SingleDot) -> Dict[str, Any]:
        """Convert SingleDot to dictionary."""
        return dot.to_dict()

    @staticmethod
    def single_dot_from_dict(data: Dict[str, Any]) -> SingleDot:
        """Create SingleDot from dictionary with validation."""
        return SingleDot.from_dict(data)
