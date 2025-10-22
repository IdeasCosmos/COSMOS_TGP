"""SJZIP chunk encoding/decoding utilities with security hardening."""

from __future__ import annotations

import struct
import logging
from dataclasses import dataclass
from typing import Iterable, List
from pathlib import Path

from .alphabet import ALPHABET_SIZE, INDEX_TO_CHAR, ensure_supported, validate_text
from .mapper import SpiralSpaceMapperExtended
from .front_space import front_order, front_position

# Security constants
CHUNK_SIZE = 500
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10 MB per chunk
_HEADER_MAGIC = b"SJZ1"
_BASE = ALPHABET_SIZE

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class DotRecord:
    """Encoded DOT data for a chunk (validated)."""

    front_index: int
    length: int
    x: float
    y: float
    z: float
    t: float
    payload: bytes

    def __post_init__(self):
        """Validate record data for security."""
        if not (0 <= self.front_index < ALPHABET_SIZE):
            raise ValueError(f"Invalid front_index: {self.front_index}")
        if not (1 <= self.length <= CHUNK_SIZE):
            raise ValueError(f"Invalid length: {self.length}")
        if len(self.payload) > MAX_PAYLOAD_SIZE:
            raise ValueError(f"Payload exceeds maximum size: {len(self.payload)}")
        if not all(0 <= coord <= 1 for coord in [self.x, self.y, self.z, self.t]):
            raise ValueError("Coordinates must be in [0, 1] range")

    def to_bytes(self) -> bytes:
        """Serialize record to bytes with validation."""
        if len(self.payload) > MAX_PAYLOAD_SIZE:
            raise ValueError("Payload too large for serialization")

        parts = [
            struct.pack(
                ">HHddddI",
                self.front_index,
                self.length,
                self.x,
                self.y,
                self.z,
                self.t,
                len(self.payload),
            ),
            self.payload,
        ]
        return b"".join(parts)

    @staticmethod
    def from_bytes(data: memoryview) -> tuple["DotRecord", memoryview]:
        """
        Deserialize record from bytes with security validation.

        Args:
            data: Memory view of bytes to parse

        Returns:
            Tuple of (DotRecord, remaining data)

        Raises:
            ValueError: If data is invalid or malformed
        """
        header_size = struct.calcsize(">HHddddI")

        if len(data) < header_size:
            raise ValueError(f"Insufficient data for header: {len(data)} < {header_size}")

        header = data[:header_size]
        try:
            front_index, length, x, y, z, t, payload_len = struct.unpack(">HHddddI", header)
        except struct.error as exc:
            raise ValueError(f"Failed to unpack header: {exc}") from exc

        # Security validations
        if payload_len > MAX_PAYLOAD_SIZE:
            raise ValueError(f"Payload length {payload_len} exceeds maximum")

        payload_start = header_size
        payload_end = payload_start + payload_len

        if len(data) < payload_end:
            raise ValueError(f"Insufficient data for payload: {len(data)} < {payload_end}")

        payload = bytes(data[payload_start:payload_end])
        rest = data[payload_end:]

        # Validation happens in __post_init__
        return DotRecord(front_index, length, x, y, z, t, payload), rest


class SJZIPCodec:
    """Encodes text into DOT records and decodes back with security."""

    def __init__(self) -> None:
        """Initialize codec with secure mapper."""
        self.mapper = SpiralSpaceMapperExtended()

    @staticmethod
    def _digits_from_text(front_char: str, text: str) -> List[int]:
        """
        Convert text to digit indices with validation.

        Args:
            front_char: Front character
            text: Text to convert

        Returns:
            List of digit indices

        Raises:
            ValueError: If text contains unsupported characters
        """
        if not text:
            raise ValueError("Text cannot be empty")

        validate_text(text, max_length=CHUNK_SIZE)
        order_map = front_order(front_char)
        digits: List[int] = []

        for char in text:
            ensure_supported(char)
            digits.append(front_position(front_char, char))

        return digits

    @staticmethod
    def _payload_from_indices(indices: Iterable[int]) -> bytes:
        """
        Convert indices to bytes payload with overflow protection.

        Args:
            indices: Iterable of indices

        Returns:
            Bytes representation

        Raises:
            ValueError: If indices are invalid
        """
        indices_list = list(indices)

        # Validate indices
        for idx in indices_list:
            if not (0 <= idx < _BASE):
                raise ValueError(f"Invalid index {idx}, must be in [0, {_BASE})")

        # Calculate value with overflow protection
        value = 0
        max_safe_value = 2 ** (MAX_PAYLOAD_SIZE * 8)  # Maximum value for payload size

        for idx in indices_list:
            new_value = value * _BASE + idx
            if new_value > max_safe_value:
                raise ValueError("Value overflow in payload encoding")
            value = new_value

        if value == 0:
            return b"\x00"

        length = (value.bit_length() + 7) // 8

        if length > MAX_PAYLOAD_SIZE:
            raise ValueError(f"Payload length {length} exceeds maximum")

        return value.to_bytes(length, "big")

    @staticmethod
    def _indices_from_payload(payload: bytes, length: int) -> List[int]:
        """
        Convert bytes payload back to indices with validation.

        Args:
            payload: Bytes to convert
            length: Expected number of indices

        Returns:
            List of indices

        Raises:
            ValueError: If payload is invalid or length mismatch
        """
        if not payload:
            raise ValueError("Payload cannot be empty")
        if length <= 0 or length > CHUNK_SIZE:
            raise ValueError(f"Invalid length: {length}")
        if len(payload) > MAX_PAYLOAD_SIZE:
            raise ValueError("Payload exceeds maximum size")

        value = int.from_bytes(payload, "big")
        indices = [0] * length

        for pos in reversed(range(length)):
            indices[pos] = value % _BASE
            value //= _BASE

        if value != 0:
            raise ValueError("Payload contained excess data beyond expected length")

        return indices

    def encode_chunk(self, text: str) -> DotRecord:
        """
        Encode text chunk to DOT record with validation.

        Args:
            text: Text to encode (max CHUNK_SIZE characters)

        Returns:
            DotRecord containing encoded data

        Raises:
            ValueError: If text is invalid
        """
        if not text:
            raise ValueError("Chunk text must be non-empty")
        if len(text) > CHUNK_SIZE:
            raise ValueError(f"Chunk exceeds maximum size: {len(text)} > {CHUNK_SIZE}")

        validate_text(text, max_length=CHUNK_SIZE)

        front_char = text[0]
        digits = self._digits_from_text(front_char, text)
        payload = self._payload_from_indices(digits)

        last_char = text[-1]
        props = self.mapper.get_properties(last_char)
        front_index = self.mapper.get_front_id(front_char)

        return DotRecord(
            front_index=front_index,
            length=len(text),
            x=props.x,
            y=props.y,
            z=props.z,
            t=props.t,
            payload=payload,
        )

    def decode_chunk(self, record: DotRecord) -> str:
        """
        Decode DOT record to text with validation.

        Args:
            record: DotRecord to decode

        Returns:
            Decoded text string

        Raises:
            ValueError: If record is invalid
        """
        if record.front_index >= ALPHABET_SIZE:
            raise ValueError(f"Invalid front_index: {record.front_index}")

        front_char = INDEX_TO_CHAR[record.front_index]
        order_map = front_order(front_char)
        digits = self._indices_from_payload(record.payload, record.length)

        chars: List[str] = []
        for digit in digits:
            if digit >= len(order_map):
                raise ValueError(f"Decoded digit {digit} outside front order")
            chars.append(order_map[digit])

        return "".join(chars)

    def encode_to_file(self, text: str, path: str) -> None:
        """
        Encode text to file with security validation.

        Args:
            text: Text to encode
            path: Output file path

        Raises:
            ValueError: If text or path is invalid
            OSError: If file operations fail
        """
        # Validate text size
        text_size = len(text.encode('utf-8'))
        if text_size > MAX_FILE_SIZE:
            raise ValueError(f"Text size {text_size} exceeds maximum {MAX_FILE_SIZE}")

        validate_text(text)

        # Validate path (prevent path traversal)
        file_path = Path(path).resolve()
        if not file_path.name.endswith('.sjz'):
            logger.warning(f"Output file {file_path.name} does not have .sjz extension")

        try:
            with open(file_path, "wb") as fh:
                fh.write(_HEADER_MAGIC)
                fh.write(struct.pack(">H", CHUNK_SIZE))

                for start in range(0, len(text), CHUNK_SIZE):
                    chunk = text[start : start + CHUNK_SIZE]
                    record = self.encode_chunk(chunk)
                    fh.write(record.to_bytes())

            logger.info(f"Successfully encoded {len(text)} characters to {file_path}")

        except Exception as exc:
            logger.error(f"Failed to encode to file {path}: {exc}")
            raise

    def decode_from_file(self, path: str) -> str:
        """
        Decode text from file with security validation.

        Args:
            path: Input file path

        Returns:
            Decoded text

        Raises:
            ValueError: If file is invalid
            OSError: If file operations fail
        """
        # Validate path
        file_path = Path(path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file size before reading
        file_size = file_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File size {file_size} exceeds maximum {MAX_FILE_SIZE}")

        try:
            with open(file_path, "rb") as fh:
                data = fh.read()

        except Exception as exc:
            logger.error(f"Failed to read file {path}: {exc}")
            raise

        mv = memoryview(data)

        # Validate header
        if len(mv) < 4 or mv[:4].tobytes() != _HEADER_MAGIC:
            raise ValueError("Invalid SJZIP file: bad magic header")

        mv = mv[4:]

        if len(mv) < 2:
            raise ValueError("Invalid SJZIP file: truncated header")

        chunk_size, = struct.unpack(">H", mv[:2])
        if chunk_size != CHUNK_SIZE:
            raise ValueError(f"Unsupported chunk size: {chunk_size}")

        mv = mv[2:]

        text_chunks: List[str] = []
        chunk_count = 0
        max_chunks = MAX_FILE_SIZE // 10  # Prevent memory exhaustion

        while mv:
            if chunk_count >= max_chunks:
                raise ValueError(f"Too many chunks: {chunk_count}")

            try:
                record, mv = DotRecord.from_bytes(mv)
                text_chunks.append(self.decode_chunk(record))
                chunk_count += 1
            except Exception as exc:
                logger.error(f"Failed to decode chunk {chunk_count}: {exc}")
                raise

        result = "".join(text_chunks)
        logger.info(f"Successfully decoded {len(result)} characters from {file_path}")

        return result
