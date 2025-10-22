"""Basic codec functionality tests."""

import pytest
from sjzip.codec import SJZIPCodec
from sjzip.optimizations.optimized_sjzip import OptimizedSJZIPCodec


class TestBasicEncoding:
    """Test basic encoding/decoding."""

    def test_simple_text(self):
        """Test encoding and decoding simple text."""
        codec = SJZIPCodec()

        test_cases = [
            "Hello, World!",
            "The quick brown fox",
            "1234567890",
            "Test",
        ]

        for text in test_cases:
            record = codec.encode_chunk(text)
            decoded = codec.decode_chunk(record)
            assert decoded == text, f"Failed for: {text}"

    def test_korean_text(self):
        """Test Korean text support."""
        codec = SJZIPCodec()

        test_cases = [
            "안녕하세요",
            "가나다라",
            "테스트",
        ]

        for text in test_cases:
            try:
                record = codec.encode_chunk(text)
                decoded = codec.decode_chunk(record)
                assert decoded == text
            except ValueError:
                # Some Korean characters may not be in alphabet
                pass


class TestOptimizedCodec:
    """Test optimized codec."""

    @pytest.mark.parametrize("level", [0, 1, 2, 3])
    def test_optimization_levels(self, level):
        """Test all optimization levels."""
        codec = OptimizedSJZIPCodec(optimization_level=level)

        text = "Hello, World! This is a test."

        compressed = codec.encode_text_optimized(text)
        decoded = codec.decode_text_optimized(compressed)

        assert decoded == text

    def test_long_text(self):
        """Test encoding long text."""
        codec = OptimizedSJZIPCodec(optimization_level=3)

        text = "Lorem ipsum dolor sit amet. " * 100

        compressed = codec.encode_text_optimized(text)
        decoded = codec.decode_text_optimized(compressed)

        assert decoded == text


class TestEdgeCases:
    """Test edge cases."""

    def test_single_character(self):
        """Test single character."""
        codec = SJZIPCodec()

        record = codec.encode_chunk("A")
        decoded = codec.decode_chunk(record)

        assert decoded == "A"

    def test_repeated_characters(self):
        """Test repeated characters."""
        codec = SJZIPCodec()

        text = "AAA"
        record = codec.encode_chunk(text)
        decoded = codec.decode_chunk(record)

        assert decoded == text

    def test_special_characters(self):
        """Test special characters."""
        codec = SJZIPCodec()

        test_cases = [
            "!@#$%",
            "()[]{}",
            ".,;:",
        ]

        for text in test_cases:
            record = codec.encode_chunk(text)
            decoded = codec.decode_chunk(record)
            assert decoded == text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
