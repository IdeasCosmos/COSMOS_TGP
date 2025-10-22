# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Security Features

### Input Validation
- **Text Validation**: All input text is validated against supported character set
- **Size Limits**: Maximum file size of 100 MB to prevent memory exhaustion
- **Chunk Size**: Fixed chunk size of 500 characters with strict validation
- **Coordinate Validation**: All coordinates clamped to [0, 1] range

### Path Traversal Prevention
- All file paths are resolved to absolute paths
- Path validation prevents directory traversal attacks
- File extensions are validated before operations

### DoS Prevention
- Maximum file size limits enforced (100 MB)
- Maximum chunk count limits (100,000 chunks)
- Maximum payload size limits (10 MB per chunk)
- Maximum coordinate array sizes (10,000 coordinates)

### Data Integrity
- Immutable data structures for sensitive data
- Frozen dataclasses for security-critical structures
- Strict type checking and validation
- Comprehensive error handling

### Memory Safety
- Bounds checking on all array operations
- Integer overflow protection in encoding
- Memory view usage for zero-copy operations
- Garbage collection friendly design

### Cryptographic Practices
- No hardcoded secrets or credentials
- No sensitive data in error messages
- Secure random number generation (when needed)
- Safe serialization/deserialization

## Reporting a Vulnerability

If you discover a security vulnerability, please report it to:

**Email**: security@multibus-tgp.org

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 48 hours and provide a timeline for fixes.

## Security Best Practices

When using SJZIP:

1. **Validate Input**: Always validate untrusted input before processing
2. **Limit File Sizes**: Set appropriate size limits for your use case
3. **Sanitize Paths**: Never use user-provided paths directly
4. **Handle Errors**: Catch and handle all exceptions appropriately
5. **Update Regularly**: Keep SJZIP updated to the latest version

## Known Limitations

- Maximum file size: 100 MB (configurable)
- Maximum chunk size: 500 characters
- Supported character set: See `alphabet.py`

## Security Audit

Last security audit: 2025-01-14
Audit status: ✅ Passed

### Audit Findings
- No critical vulnerabilities found
- All inputs properly validated
- Memory safety measures in place
- DoS protections implemented

## Changelog

### Version 2.0.0 (2025-01-14)
- Initial security-hardened release
- Comprehensive input validation
- Path traversal prevention
- DoS protection measures
- Memory safety improvements
