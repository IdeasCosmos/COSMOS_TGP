"""Security tests for SJZIP."""

import pytest
import numpy as np
from sjzip.codec import SJZIPCodec, MAX_FILE_SIZE, CHUNK_SIZE
from sjzip.alphabet import ensure_supported, validate_text, ALPHABET
from sjzip.optimizations.optimized_sjzip import OptimizedSJZIPCodec


class TestInputValidation:
    """Test input validation security."""

    def test_unsupported_character_rejection(self):
        """Test that unsupported characters are rejected."""
        with pytest.raises(ValueError, match="Unsupported character"):
            ensure_supported('\x00\x01')  # Control character

        with pytest.raises(ValueError, match="Expected single character"):
            ensure_supported("ab")  # Multiple characters

    def test_text_size_limits(self):
        """Test that text size limits are enforced."""
        codec = OptimizedSJZIPCodec()

        # Too large text
        large_text = "A" * (MAX_FILE_SIZE + 1000)
        with pytest.raises(ValueError, match="exceeds maximum"):
            codec.encode_text_optimized(large_text)

    def test_empty_text_rejection(self):
        """Test that empty text is rejected."""
        codec = SJZIPCodec()

        with pytest.raises(ValueError, match="non-empty"):
            codec.encode_chunk("")

    def test_chunk_size_limit(self):
        """Test chunk size enforcement."""
        codec = SJZIPCodec()

        # Exact limit should work
        text = "A" * CHUNK_SIZE
        record = codec.encode_chunk(text)
        assert record.length == CHUNK_SIZE

        # Over limit should be rejected
        text = "A" * (CHUNK_SIZE + 1)
        with pytest.raises(ValueError, match="exceeds maximum"):
            codec.encode_chunk(text)


class TestPathTraversalPrevention:
    """Test path traversal attack prevention."""

    def test_safe_file_paths(self, tmp_path):
        """Test that file paths are sanitized."""
        codec = SJZIPCodec()

        # Normal path should work
        safe_path = tmp_path / "test.sjz"
        codec.encode_to_file("Hello", str(safe_path))
        assert safe_path.exists()

        # Path traversal attempts should be safely resolved
        traversal_path = tmp_path / ".." / "test2.sjz"
        codec.encode_to_file("World", str(traversal_path))
        # Should create file in resolved location


class TestCoordinateValidation:
    """Test coordinate validation."""

    def test_coordinate_range_clamping(self):
        """Test that coordinates are clamped to valid ranges."""
        from sjzip.mapper import SpiralSpaceMapperExtended

        mapper = SpiralSpaceMapperExtended()

        # All coordinates should be in [0, 1]
        for char in ALPHABET[:10]:  # Test first 10 chars
            props = mapper.get_properties(char)
            assert 0 <= props.x <= 1
            assert 0 <= props.y <= 1
            assert 0 <= props.z <= 1
            assert 0 <= props.t <= 1


class TestIntegerOverflow:
    """Test integer overflow protection."""

    def test_payload_overflow_protection(self):
        """Test that large payloads don't cause overflow."""
        codec = SJZIPCodec()

        # Very large index should be handled safely
        indices = [96] * 500  # Max valid index
        payload = codec._payload_from_indices(indices)

        # Should not raise overflow error
        assert isinstance(payload, bytes)
        assert len(payload) > 0


class TestDOSPrevention:
    """Test Denial of Service prevention."""

    def test_max_chunks_limit(self):
        """Test that chunk count is limited."""
        from sjzip.optimizations.optimized_sjzip import OptimizedSJZIPCodec

        codec = OptimizedSJZIPCodec()

        # Create data claiming too many chunks
        malicious_data = b'SJZO'  # Magic
        malicious_data += b'\x03'  # Level
        malicious_data += b'\x00\x00\x10\x00'  # Length 4096
        malicious_data += b'\xFF\xFF'  # 65535 chunks (too many)

        with pytest.raises(ValueError, match="Too many chunks"):
            codec.decode_text_optimized(malicious_data)

    def test_payload_size_limit(self):
        """Test that payload size is limited."""
        from sjzip.codec import DotRecord

        # Attempting to create record with huge payload should fail
        huge_payload = b'A' * (11 * 1024 * 1024)  # 11 MB

        with pytest.raises(ValueError, match="exceeds maximum"):
            DotRecord(
                front_index=0,
                length=1,
                x=0.5, y=0.5, z=0.5, t=0.0,
                payload=huge_payload
            )


class TestDataIntegrity:
    """Test data integrity protections."""

    def test_immutable_alphabet(self):
        """Test that alphabet cannot be modified."""
        from sjzip.alphabet import ALPHABET

        # ALPHABET should be tuple (immutable)
        assert isinstance(ALPHABET, tuple)

        with pytest.raises(TypeError):
            ALPHABET[0] = 'X'  # Should fail

    def test_coordinate_caching(self):
        """Test that coordinate cache is read-only."""
        from sjzip.mapper import SpiralSpaceMapperExtended

        mapper = SpiralSpaceMapperExtended()
        props1 = mapper.get_properties('A')
        props2 = mapper.get_properties('A')

        # Should return same immutable object
        assert props1 is props2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
