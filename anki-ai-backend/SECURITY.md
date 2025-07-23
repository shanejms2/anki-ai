# Security Features Documentation

## Overview

The Anki-AI backend implements comprehensive security measures to protect against common web application vulnerabilities and ensure data integrity.

## 🔒 Rate Limiting & Request Throttling

### Implementation
- **In-memory rate limiter** with sliding window algorithm
- **Burst protection** to prevent rapid-fire requests
- **Automatic cleanup** of expired request records
- **Per-endpoint configuration** with different limits

### Rate Limits by Endpoint

#### Authentication Endpoints
- **Login**: 5 requests per 5 minutes, 3 per minute burst
- **Register**: 3 requests per hour, 1 per minute burst
- **Password Reset**: 3 requests per hour, 1 per minute burst
- **Token Refresh**: 10 requests per 5 minutes, 5 per minute burst

#### Card Management
- **Create Cards**: 20 requests per 5 minutes, 5 per minute burst
- **Update Cards**: 30 requests per 5 minutes, 10 per minute burst
- **Delete Cards**: 10 requests per 5 minutes, 3 per minute burst
- **List Cards**: 100 requests per 5 minutes, 20 per minute burst
- **Get Card**: 200 requests per 5 minutes, 50 per minute burst

#### Review System
- **Submit Reviews**: 50 requests per 5 minutes, 10 per minute burst
- **List Reviews**: 100 requests per 5 minutes, 20 per minute burst
- **Review Stats**: 30 requests per 5 minutes, 10 per minute burst

#### System Operations
- **Cache Stats**: 10 requests per 5 minutes, 3 per minute burst
- **Cache Clear**: 2 requests per hour, 1 per minute burst
- **Cache Cleanup**: 5 requests per hour, 2 per minute burst

### Response Headers
Rate limit information is included in response headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Timestamp when limit resets
- `X-RateLimit-Burst-Limit`: Burst limit (if configured)
- `X-RateLimit-Burst-Remaining`: Remaining burst requests

## 🧹 Input Sanitization & Validation

### Sanitization Types

#### Text Sanitization
- **HTML Encoding**: Prevents XSS attacks
- **Control Character Removal**: Removes dangerous control chars
- **Pattern Filtering**: Blocks SQL injection and command injection
- **Length Limiting**: Prevents buffer overflow attacks
- **Whitespace Normalization**: Consistent formatting

#### HTML Content Sanitization
- **Allowed Tags**: `p`, `br`, `strong`, `em`, `u`, `ol`, `ul`, `li`, `h1-h6`
- **Script Removal**: Blocks `<script>`, `javascript:`, `vbscript:`
- **Form Removal**: Prevents form injection attacks
- **Style Filtering**: Blocks dangerous CSS

#### Email Validation
- **Format Validation**: RFC-compliant email format
- **Length Limits**: Maximum 254 characters
- **Character Filtering**: Removes dangerous characters
- **Case Normalization**: Converts to lowercase

#### URL Validation
- **Protocol Whitelist**: Only `http://`, `https://`, relative URLs
- **Dangerous Protocol Blocking**: Blocks `javascript:`, `data:`, `file:`
- **URL Encoding**: Prevents injection attacks
- **Path Traversal Protection**: Blocks `../` attempts

#### Filename Sanitization
- **Dangerous Character Removal**: Blocks `<>:"/\|?*` and control chars
- **Path Traversal Protection**: Blocks `../` and `..\`
- **Length Limiting**: Maximum 255 characters
- **Extension Preservation**: Maintains file extensions

### Validation Rules

#### User Data
- **Username**: 3-50 characters
- **Email**: Valid format, max 254 characters
- **Password**: 8-128 characters

#### Card Data
- **Front Content**: 1-5000 characters
- **Back Content**: 1-10000 characters
- **Tags**: Max 100 characters per tag

#### Review Data
- **Rating**: 1-5 (integer)
- **Card ID**: Valid UUID format

#### Pagination
- **Page Size**: 1-100 items
- **Page Number**: Positive integer

## 🛡️ Security Headers

### HTTP Security Headers
- **X-Content-Type-Options**: `nosniff` - Prevents MIME type sniffing
- **X-Frame-Options**: `DENY` - Prevents clickjacking
- **X-XSS-Protection**: `1; mode=block` - XSS protection
- **Referrer-Policy**: `strict-origin-when-cross-origin` - Controls referrer info
- **Content-Security-Policy**: Restricts resource loading

### Custom Headers
- **X-Process-Time**: Request processing time
- **X-RateLimit-***: Rate limiting information

## 📊 Request/Response Logging

### Logged Information
- **Request Details**: Method, path, client IP, user agent
- **Response Details**: Status code, processing time
- **Error Information**: Exception details, stack traces
- **Security Events**: Rate limit violations, validation failures

### Log Format
Structured JSON logging with:
- Timestamp
- Log level
- Event description
- Context data
- Error details (when applicable)

## 🔐 Authentication & Authorization

### JWT Token Security
- **Secure Token Storage**: HTTP-only cookies or secure headers
- **Token Expiration**: Configurable expiration times
- **Token Refresh**: Secure refresh mechanism
- **Token Validation**: Signature verification and payload validation

### User Session Management
- **Session Tracking**: User activity monitoring
- **Concurrent Session Control**: Configurable session limits
- **Session Invalidation**: Secure logout and token blacklisting

## 🗄️ Database Security

### Row Level Security (RLS)
- **User Isolation**: Users can only access their own data
- **Card Ownership**: Cards are isolated by user
- **Review Isolation**: Reviews are isolated by user
- **System Operations**: Admin-only system endpoints

### SQL Injection Prevention
- **Parameterized Queries**: All database queries use parameters
- **Input Sanitization**: All user input is sanitized
- **Query Validation**: Query structure validation
- **Error Handling**: Generic error messages (no SQL details)

## 🚀 Performance & Monitoring

### Caching Security
- **Cache Isolation**: User-specific cache keys
- **Cache Invalidation**: Secure cache clearing
- **Cache Statistics**: Performance monitoring
- **Memory Management**: Automatic cleanup of expired entries

### Monitoring & Alerts
- **Rate Limit Violations**: Automatic logging and alerting
- **Input Validation Failures**: Tracking of malicious input
- **Performance Metrics**: Response time monitoring
- **Error Tracking**: Comprehensive error logging

## 🧪 Security Testing

### Automated Tests
- **Rate Limiting Tests**: Verify limit enforcement
- **Input Validation Tests**: Test sanitization effectiveness
- **Authentication Tests**: Verify access controls
- **SQL Injection Tests**: Verify injection prevention

### Manual Testing
- **Penetration Testing**: Regular security assessments
- **Code Reviews**: Security-focused code review process
- **Dependency Scanning**: Regular vulnerability scanning

## 📋 Security Checklist

### Implementation Status
- ✅ Rate limiting and request throttling
- ✅ Input sanitization and validation
- ✅ Security headers implementation
- ✅ Request/response logging
- ✅ Authentication and authorization
- ✅ Database security (RLS)
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CSRF protection
- ✅ Error handling without information disclosure

### Ongoing Security Measures
- 🔄 Regular dependency updates
- 🔄 Security monitoring and alerting
- 🔄 Penetration testing
- 🔄 Code security reviews
- 🔄 User activity monitoring

## 🚨 Incident Response

### Security Incident Types
1. **Rate Limit Violations**: Excessive request attempts
2. **Input Validation Failures**: Malicious input detection
3. **Authentication Failures**: Invalid login attempts
4. **Authorization Violations**: Unauthorized access attempts

### Response Procedures
1. **Immediate Response**: Block malicious IPs/users
2. **Investigation**: Analyze logs and determine scope
3. **Mitigation**: Apply security patches and updates
4. **Recovery**: Restore normal operations
5. **Post-Incident**: Document lessons learned

## 📞 Security Contact

For security issues or questions:
- **Email**: security@anki-ai.com
- **Bug Reports**: Use the security issue template
- **Responsible Disclosure**: Follow responsible disclosure guidelines

---

*This document is maintained by the Anki-AI development team and should be updated with any security changes.* 