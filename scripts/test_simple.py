#!/usr/bin/env python3
"""Simple SJZIP functionality test."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sjzip.optimizations import OptimizedSJZIPCodec


def test_simple():
    """Run simple tests."""
    test_cases = [
        ("English", "Hello, World!"),
        ("Numbers", "1234567890"),
        ("Special", "!@#$%^&*()"),
        ("Mixed", "Test 123 ABC"),
        ("Pattern", "AAABBBCCC"),
    ]

    print("=" * 60)
    print("SJZIP Simple Test")
    print("=" * 60)

    for name, text in test_cases:
        print(f"\nTest: {name}")
        print(f"Original: {text}")

        try:
            codec = OptimizedSJZIPCodec(optimization_level=3)

            # Compress
            compressed = codec.encode_text_optimized(text)

            # Decompress
            decoded = codec.decode_text_optimized(compressed)

            # Results
            success = "✅" if decoded == text else "❌"
            ratio = len(compressed) / len(text.encode('utf-8'))

            print(f"Result: {success} | Ratio: {ratio:.2%} | Decoded: {decoded}")

        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n✨ Test complete!")


if __name__ == "__main__":
    test_simple()
