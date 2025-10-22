"""Extended alphabet for SJZIP with security validations."""

from __future__ import annotations

from typing import Dict, List, FrozenSet

# Printable ASCII 32-126 plus NULL (0) at the front
_BASE_PRINTABLE = [chr(i) for i in range(32, 127)]

# Korean characters (common Hangul)
_KOREAN_CHARS = [
    # 자주 사용되는 한글 자모
    'ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ',
    'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅣ',
    # 자주 사용되는 완성형 한글
    '가', '나', '다', '라', '마', '바', '사', '아', '자', '차', '카', '타', '파', '하',
    '고', '노', '도', '로', '모', '보', '소', '오', '조', '초', '코', '토', '포', '호',
    '구', '누', '두', '루', '무', '부', '수', '우', '주', '추', '쿠', '투', '푸', '후',
    '그', '는', '드', '르', '므', '브', '스', '으', '즈', '츠', '크', '트', '프', '흐',
    '기', '니', '디', '리', '미', '비', '시', '이', '지', '치', '키', '티', '피', '히',
    # 자주 사용되는 단어들의 글자
    '안', '녕', '하', '세', '요', '습', '니', '다', '입', '것', '은', '를', '의', '에',
    '와', '과', '할', '수', '있', '었', '였', '을', '를', '이', '가', '에', '서', '도',
    '지', '만', '까', '를', '위', '해', '되', '된', '한', '합', '같', '음', '임', '함',
]

# Additional characters
_EXTRA_CHARS = [
    "\r", "\n", "\t",
    "£", "â", "æ", "è", "é", "Œ", "œ",
    "η", "ο", "σ", "τ", "ς", "ϰ",
    "ו", "ח",
    "—", "'", "'", """, """, "•", "™",
]

# Build alphabet ensuring uniqueness
_ALPHABET: List[str] = [chr(0)]
_seen = set(_ALPHABET)

for char in _BASE_PRINTABLE + _KOREAN_CHARS + _EXTRA_CHARS:
    if char not in _seen:
        _ALPHABET.append(char)
        _seen.add(char)

# Immutable exports for security
ALPHABET: tuple = tuple(_ALPHABET)
ALPHABET_SIZE: int = len(ALPHABET)
CHAR_TO_INDEX: Dict[str, int] = {char: idx for idx, char in enumerate(ALPHABET)}
INDEX_TO_CHAR: Dict[int, str] = {idx: char for char, idx in CHAR_TO_INDEX.items()}
SUPPORTED_CHARS: FrozenSet[str] = frozenset(ALPHABET)


def ensure_supported(char: str) -> None:
    """
    Validate that character is in the extended alphabet.

    Args:
        char: Single character to validate

    Raises:
        ValueError: If character is not supported
        TypeError: If input is not a string
    """
    if not isinstance(char, str):
        raise TypeError(f"Expected string, got {type(char).__name__}")

    if len(char) != 1:
        raise ValueError(f"Expected single character, got string of length {len(char)}")

    if char not in SUPPORTED_CHARS:
        # Sanitize error message to prevent information leakage
        char_repr = repr(char) if ord(char) < 128 else f"U+{ord(char):04X}"
        raise ValueError(f"Unsupported character: {char_repr}")


def validate_text(text: str, max_length: int = 1000000) -> None:
    """
    Validate entire text string for security.

    Args:
        text: Text to validate
        max_length: Maximum allowed length (default 1MB of chars)

    Raises:
        ValueError: If text contains unsupported characters
        TypeError: If input is not a string
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected string, got {type(text).__name__}")

    if len(text) > max_length:
        raise ValueError(f"Text exceeds maximum length of {max_length} characters")

    # Find first unsupported character for better error reporting
    for idx, char in enumerate(text):
        if char not in SUPPORTED_CHARS:
            char_repr = repr(char) if ord(char) < 128 else f"U+{ord(char):04X}"
            raise ValueError(
                f"Unsupported character {char_repr} at position {idx}"
            )
