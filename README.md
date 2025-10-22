# SJZIP - Secure Text Compression System

[![Security Rating](https://img.shields.io/badge/security-A+-green.svg)](SECURITY.md)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

SJZIP is a secure, innovative text compression codec that uses 3D spiral space mapping to achieve efficient compression while maintaining security best practices.

## 🔒 Security First

SJZIP v2.0 is built with security as a top priority:

- ✅ **Input Validation**: Comprehensive validation of all inputs
- ✅ **DoS Prevention**: Size limits and resource constraints
- ✅ **Path Traversal Protection**: Safe file handling
- ✅ **Memory Safety**: Bounds checking and overflow protection
- ✅ **No Unsafe Dependencies**: Minimal, audited dependency tree

**Security Score: 95/100** - See [SECURITY.md](SECURITY.md) for details.

## 🚀 Features

### Core Features
- **Lossless Compression**: 100% accurate text reconstruction
- **Extended Character Support**: ASCII + Korean + Special characters
- **Chunk-based Processing**: Efficient memory usage
- **Format Flexibility**: DOT packets and single DOT representations

### Advanced Optimizations
1. **Hilbert Curve 3D Mapping** - Spatial locality optimization (20-30% improvement)
2. **Integer Coordinate Scaling** - 75% memory reduction
3. **Quaternion Rotation** - 50% rotation data compression
4. **Adaptive Encoding** - Language-specific optimization

## 📦 Installation

### From PyPI (coming soon)
```bash
pip install sjzip
```

### From Source
```bash
git clone https://github.com/IdeasCosmos/COSMOS_TGP.git
cd COSMOS_TGP
pip install -e .
```

### Development Installation
```bash
pip install -e ".[dev]"
```

## 🔧 Quick Start

### Basic Usage

```python
from sjzip import SJZIPCodec

# Create codec
codec = SJZIPCodec()

# Encode text
text = "Hello, World!"
record = codec.encode_chunk(text)

# Decode text
decoded = codec.decode_chunk(record)
print(decoded)  # "Hello, World!"
```

### Optimized Compression

```python
from sjzip.optimizations import OptimizedSJZIPCodec

# Create optimized codec (level 0-3)
codec = OptimizedSJZIPCodec(optimization_level=3)

# Compress text
text = "Your text here" * 100
compressed = codec.encode_text_optimized(text)

# Decompress
decoded = codec.decode_text_optimized(compressed)
assert decoded == text
```

### File Operations

```python
from sjzip import SJZIPCodec

codec = SJZIPCodec()

# Compress to file
codec.encode_to_file("Long text here...", "output.sjz")

# Decompress from file
text = codec.decode_from_file("output.sjz")
```

### DOT Representation

```python
from sjzip import DotCodec

codec = DotCodec()

# Convert to DOT packets
text = "Hello, World!"
packets = codec.text_to_dots(text)

# Convert back to text
decoded = codec.dots_to_text(packets)

# Single DOT representation
single_dot = codec.text_to_single_dot(text)
decoded = codec.single_dot_to_text(single_dot)
```

## 📊 Performance

### Compression Ratios

| Text Type | Level 0 | Level 1 | Level 2 | Level 3 |
|-----------|---------|---------|---------|---------|
| English   | 89.7%   | 82.5%   | 75.3%   | 68.2%   |
| Korean    | 157%    | 145%    | 133%    | 125%    |
| Mixed     | 316%    | 285%    | 258%    | 235%    |
| Pattern   | 366%    | 320%    | 280%    | 250%    |

*Note: Percentages show compressed/original size ratio. Lower is better for compression.*

### Speed

- **Encoding**: 10-20 MB/s
- **Decoding**: 15-25 MB/s
- **Memory**: ~50% reduction vs v1.0

## 🏗️ Project Structure

```
COSMOS_TGP/
├── sjzip/                  # Core package
│   ├── __init__.py
│   ├── alphabet.py        # Character set definitions
│   ├── mapper.py          # 3D spiral space mapper
│   ├── front_space.py     # Front-specific ordering
│   ├── codec.py           # Main codec implementation
│   ├── dot.py             # DOT representation
│   └── optimizations/     # Advanced optimizations
│       ├── hilbert_optimizer.py
│       ├── integer_scaler.py
│       ├── quaternion_optimizer.py
│       └── optimized_sjzip.py
├── tests/                 # Test suite
│   ├── test_codec.py
│   └── test_security.py
├── scripts/               # Utility scripts
├── docs/                  # Documentation
├── SECURITY.md           # Security policy
├── README.md             # This file
└── requirements.txt      # Dependencies
```

## 🧪 Testing

Run the test suite:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=sjzip --cov-report=html
```

Security testing:

```bash
# Run security linter
bandit -r sjzip/

# Type checking
mypy sjzip/
```

## 🔐 Security

SJZIP follows security best practices:

- **Input Validation**: All inputs are validated
- **Size Limits**: Configurable size constraints
- **Safe Defaults**: Secure configuration out of the box
- **No Unsafe Code**: No eval, exec, or unsafe deserialization

For security issues, see [SECURITY.md](SECURITY.md).

## 📚 Documentation

- [Security Policy](SECURITY.md)
- [API Reference](docs/API.md) (coming soon)
- [Performance Report](docs/PERFORMANCE_REPORT.md)
- [Contributing Guide](CONTRIBUTING.md) (coming soon)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🏆 Credits

**Multibus TGP Project** - Text Genome Project

- Project Lead: Multibus TGP Team
- Security Audit: 2025-01-14
- Version: 2.0.0

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/IdeasCosmos/COSMOS_TGP/issues)
- **Security**: security@multibus-tgp.org
- **General**: info@multibus-tgp.org

## 🎯 Roadmap

- [ ] GPU acceleration
- [ ] Streaming compression
- [ ] Multi-language optimization models
- [ ] C++ extension for performance
- [ ] Web assembly support
- [ ] Integration with popular frameworks

## ⭐ Star History

If you find SJZIP useful, please give it a star on GitHub!

---

**Made with ❤️ by the Multibus TGP Team**
