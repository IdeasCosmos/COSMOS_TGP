"""SJZIP optimization integration with security."""

import struct
import time
import logging
from typing import Dict
from dataclasses import dataclass
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sjzip.codec import SJZIPCodec, DotRecord, CHUNK_SIZE, MAX_FILE_SIZE
from sjzip.alphabet import ALPHABET, CHAR_TO_INDEX, validate_text
from sjzip.mapper import SpiralSpaceMapperExtended
from sjzip.front_space import front_order

from .hilbert_optimizer import HilbertCurve3D
from .integer_scaler import IntegerCoordinateScaler
from .quaternion_optimizer import QuaternionSpiralEncoder

logger = logging.getLogger(__name__)


@dataclass
class OptimizedDotRecord:
    """Optimized DOT record with security validation."""
    front_index: int
    length: int
    hilbert_index: int
    quaternion: bytes
    compressed_payload: bytes

    def __post_init__(self):
        """Validate record."""
        if not (0 <= self.front_index < len(ALPHABET)):
            raise ValueError(f"Invalid front_index: {self.front_index}")
        if not (1 <= self.length <= CHUNK_SIZE):
            raise ValueError(f"Invalid length: {self.length}")
        if len(self.quaternion) != 6:
            raise ValueError("Quaternion must be 6 bytes")

    def to_bytes(self) -> bytes:
        """Serialize with size limits."""
        if len(self.compressed_payload) > 10 * 1024 * 1024:  # 10MB limit
            raise ValueError("Payload too large")
        
        parts = [
            struct.pack('>B', self.front_index),
            struct.pack('>H', self.length),
            self.hilbert_index.to_bytes(3, 'big'),
            self.quaternion,
            struct.pack('>I', len(self.compressed_payload)),
            self.compressed_payload
        ]
        return b''.join(parts)

    @staticmethod
    def from_bytes(data: bytes):
        """Deserialize with validation."""
        if len(data) < 16:
            raise ValueError("Insufficient data")
        
        offset = 0
        front_index = data[offset]
        offset += 1
        
        length = struct.unpack('>H', data[offset:offset+2])[0]
        offset += 2
        
        hilbert_index = int.from_bytes(data[offset:offset+3], 'big')
        offset += 3
        
        quaternion = data[offset:offset+6]
        offset += 6
        
        payload_len = struct.unpack('>I', data[offset:offset+4])[0]
        offset += 4
        
        if payload_len > 10 * 1024 * 1024:
            raise ValueError("Payload too large")
        
        if len(data) < offset + payload_len:
            raise ValueError("Truncated payload")
        
        compressed_payload = data[offset:offset+payload_len]
        offset += payload_len
        
        return OptimizedDotRecord(
            front_index=front_index,
            length=length,
            hilbert_index=hilbert_index,
            quaternion=quaternion,
            compressed_payload=compressed_payload
        ), offset


class OptimizedSJZIPCodec:
    """Secure optimized SJZIP codec."""

    MAX_TEXT_SIZE = MAX_FILE_SIZE

    def __init__(self, optimization_level: int = 3):
        if not (0 <= optimization_level <= 3):
            raise ValueError("Optimization level must be 0-3")
        
        self.optimization_level = optimization_level
        self.base_codec = SJZIPCodec()
        self.mapper = SpiralSpaceMapperExtended()
        
        if optimization_level >= 1:
            self.scaler = IntegerCoordinateScaler()
        if optimization_level >= 3:
            self.hilbert = HilbertCurve3D(order=8)
            self.quaternion_encoder = QuaternionSpiralEncoder()
        
        self.stats = {
            'original_size': 0,
            'compressed_size': 0,
            'compression_time': 0.0,
            'decompression_time': 0.0
        }

    def encode_chunk_optimized(self, text: str) -> OptimizedDotRecord:
        """Encode chunk with security validation."""
        if not text:
            raise ValueError("Text cannot be empty")
        if len(text) > CHUNK_SIZE:
            text = text[:CHUNK_SIZE]
        
        validate_text(text, max_length=CHUNK_SIZE)
        
        start_time = time.perf_counter()
        
        front_char = text[0]
        front_index = CHAR_TO_INDEX.get(front_char, 0)
        
        if self.optimization_level == 0:
            record = self.base_codec.encode_chunk(text)
            return OptimizedDotRecord(
                front_index=record.front_index,
                length=record.length,
                hilbert_index=0,
                quaternion=b'\x00' * 6,
                compressed_payload=record.payload
            )
        
        # Optimized encoding
        digits = self.base_codec._digits_from_text(front_char, text)
        base_payload = self.base_codec._payload_from_indices(digits)
        
        hilbert_index = 0
        quaternion_bytes = b'\x00' * 6
        
        if self.optimization_level >= 3:
            last_char = text[-1]
            props = self.mapper.get_properties(last_char)
            
            quat = self.quaternion_encoder.angle_radius_to_quaternion(
                props.angle_rad, props.radius, props.depth
            )
            quaternion_bytes = self.quaternion_encoder.compress_quaternion(quat)
        
        self.stats['compression_time'] = time.perf_counter() - start_time
        self.stats['original_size'] = len(text.encode('utf-8'))
        self.stats['compressed_size'] = 16 + len(base_payload)
        
        return OptimizedDotRecord(
            front_index=front_index,
            length=len(text),
            hilbert_index=hilbert_index,
            quaternion=quaternion_bytes,
            compressed_payload=base_payload
        )

    def decode_chunk_optimized(self, record: OptimizedDotRecord) -> str:
        """Decode chunk with validation."""
        start_time = time.perf_counter()
        
        if record.front_index >= len(ALPHABET):
            raise ValueError(f"Invalid front_index: {record.front_index}")
        
        front_char = ALPHABET[record.front_index]
        indices = self.base_codec._indices_from_payload(record.compressed_payload, record.length)
        
        order_map = front_order(front_char)
        chars = []
        
        for idx in indices:
            if idx < len(order_map):
                chars.append(order_map[idx])
            else:
                chars.append(chr(0))
        
        self.stats['decompression_time'] = time.perf_counter() - start_time
        return ''.join(chars)

    def encode_text_optimized(self, text: str) -> bytes:
        """Encode entire text with security limits."""
        if not text:
            raise ValueError("Text cannot be empty")
        
        text_size = len(text.encode('utf-8'))
        if text_size > self.MAX_TEXT_SIZE:
            raise ValueError(f"Text size {text_size} exceeds maximum {self.MAX_TEXT_SIZE}")
        
        validate_text(text)
        
        header = b'SJZO'
        header += struct.pack('>B', self.optimization_level)
        header += struct.pack('>I', len(text))
        
        encoded_chunks = []
        for i in range(0, len(text), CHUNK_SIZE):
            chunk = text[i:i+CHUNK_SIZE]
            record = self.encode_chunk_optimized(chunk)
            encoded_chunks.append(record.to_bytes())
        
        data = header + struct.pack('>H', len(encoded_chunks))
        
        for chunk_data in encoded_chunks:
            data += chunk_data
        
        return data

    def decode_text_optimized(self, data: bytes) -> str:
        """Decode with security validation."""
        if len(data) < 11:
            raise ValueError("Data too short")
        
        offset = 0
        
        if data[offset:offset+4] != b'SJZO':
            raise ValueError("Invalid SJZO file")
        offset += 4
        
        optimization_level = data[offset]
        offset += 1
        
        original_length = struct.unpack('>I', data[offset:offset+4])[0]
        offset += 4
        
        if original_length > self.MAX_TEXT_SIZE:
            raise ValueError("Original length too large")
        
        chunk_count = struct.unpack('>H', data[offset:offset+2])[0]
        offset += 2
        
        if chunk_count > 100000:  # Sanity limit
            raise ValueError("Too many chunks")
        
        decoded_chunks = []
        
        for _ in range(chunk_count):
            record, bytes_read = OptimizedDotRecord.from_bytes(data[offset:])
            offset += bytes_read
            
            chunk_text = self.decode_chunk_optimized(record)
            decoded_chunks.append(chunk_text)
        
        result = ''.join(decoded_chunks)
        
        if len(result) > original_length:
            result = result[:original_length]
        
        return result

    def get_compression_ratio(self) -> float:
        """Get compression ratio."""
        if self.stats['original_size'] == 0:
            return 0.0
        return self.stats['compressed_size'] / self.stats['original_size']
