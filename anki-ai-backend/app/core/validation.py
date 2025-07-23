"""
Input sanitization and validation system
Provides protection against malicious input and ensures data integrity.
"""

import re
import html
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote, unquote
from pydantic import BaseModel, validator, ValidationError
from fastapi import HTTPException, status
from app.core.logging import logger


class InputSanitizer:
    """Input sanitization utilities."""
    
    # Patterns for various types of malicious content
    SQL_INJECTION_PATTERNS = [
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
        r"(\b(and|or)\b\s+\d+\s*[=<>])",
        r"(--|#|/\*|\*/)",
        r"(\bxp_|sp_|fn_)",
        r"(\bwaitfor\b)",
        r"(\bdelay\b)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
        r"<form[^>]*>.*?</form>",
        r"<input[^>]*>",
        r"<textarea[^>]*>.*?</textarea>",
        r"<select[^>]*>.*?</select>",
        r"<button[^>]*>.*?</button>",
        r"<link[^>]*>",
        r"<meta[^>]*>",
        r"<style[^>]*>.*?</style>",
        r"javascript:",
        r"vbscript:",
        r"data:",
        r"on\w+\s*=",
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$(){}[\]]",
        r"\b(cat|ls|pwd|whoami|id|uname|ps|top|kill|rm|cp|mv|chmod|chown)\b",
        r"\b(netcat|nc|telnet|ssh|scp|wget|curl|ftp)\b",
        r"\b(echo|printf|sprintf|system|exec|shell_exec|passthru)\b",
    ]
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: int = 1000) -> str:
        """Sanitize text input by removing dangerous patterns and encoding HTML."""
        if not text:
            return ""
        
        # Convert to string if needed
        text = str(text)
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # HTML encode to prevent XSS
        text = html.escape(text, quote=True)
        
        # Remove any remaining dangerous patterns
        for pattern in cls.SQL_INJECTION_PATTERNS + cls.XSS_PATTERNS + cls.COMMAND_INJECTION_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @classmethod
    def sanitize_html(cls, html_content: str, allowed_tags: List[str] = None) -> str:
        """Sanitize HTML content by allowing only safe tags."""
        if not html_content:
            return ""
        
        if allowed_tags is None:
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        
        # Remove all tags except allowed ones
        pattern = r'<(?!\/?(?:' + '|'.join(allowed_tags) + r')\b)[^>]+>'
        sanitized = re.sub(pattern, '', html_content)
        
        # Remove any remaining script-like content
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    @classmethod
    def sanitize_url(cls, url: str) -> str:
        """Sanitize URL input."""
        if not url:
            return ""
        
        # Remove dangerous protocols
        dangerous_protocols = ['javascript:', 'vbscript:', 'data:', 'file:']
        url_lower = url.lower()
        
        for protocol in dangerous_protocols:
            if url_lower.startswith(protocol):
                return ""
        
        # Only allow http, https, and relative URLs
        if not (url_lower.startswith(('http://', 'https://', '/', './', '../'))):
            return ""
        
        # URL encode to prevent injection
        return quote(url, safe=':/?=&')
    
    @classmethod
    def sanitize_email(cls, email: str) -> str:
        """Sanitize email input."""
        if not email:
            return ""
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return ""
        
        # Remove any dangerous characters
        email = re.sub(r'[<>"\']', '', email)
        
        return email.lower().strip()
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename input."""
        if not filename:
            return ""
        
        # Remove dangerous characters
        dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
        sanitized = re.sub(dangerous_chars, '', filename)
        
        # Remove path traversal attempts
        sanitized = re.sub(r'\.\./', '', sanitized)
        sanitized = re.sub(r'\.\.\\', '', sanitized)
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = name[:255-len(ext)-1] + ('.' + ext if ext else '')
        
        return sanitized


class ValidationRules:
    """Validation rules and constraints."""
    
    # Card validation rules
    CARD_TITLE_MIN_LENGTH = 1
    CARD_TITLE_MAX_LENGTH = 200
    CARD_FRONT_MIN_LENGTH = 1
    CARD_FRONT_MAX_LENGTH = 5000
    CARD_BACK_MIN_LENGTH = 1
    CARD_BACK_MAX_LENGTH = 10000
    CARD_TAGS_MAX_LENGTH = 100
    
    # User validation rules
    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 50
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128
    EMAIL_MAX_LENGTH = 254
    
    # Review validation rules
    RATING_MIN = 1
    RATING_MAX = 5
    
    # Pagination rules
    MAX_PAGE_SIZE = 100
    DEFAULT_PAGE_SIZE = 20


class EnhancedBaseModel(BaseModel):
    """Enhanced Pydantic model with sanitization and validation."""
    
    class Config:
        extra = "forbid"  # Reject extra fields
        validate_assignment = True  # Validate on assignment
    
    @classmethod
    def sanitize_input(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        print("SANITIZE_INPUT CALLED WITH:", data)
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Apply different sanitization based on field type
                if 'email' in key.lower():
                    sanitized[key] = InputSanitizer.sanitize_email(value)
                elif 'url' in key.lower():
                    sanitized[key] = InputSanitizer.sanitize_url(value)
                elif 'filename' in key.lower():
                    sanitized[key] = InputSanitizer.sanitize_filename(value)
                elif 'html' in key.lower() or 'content' in key.lower():
                    sanitized[key] = InputSanitizer.sanitize_html(value)
                else:
                    sanitized[key] = InputSanitizer.sanitize_text(value)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_input(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.sanitize_input(item) if isinstance(item, dict)
                    else InputSanitizer.sanitize_text(str(item)) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized


def validate_and_sanitize_input(data: Dict[str, Any], model_class: type) -> Dict[str, Any]:
    """Validate and sanitize input data using a Pydantic model."""
    try:
        # Sanitize input first
        sanitized_data = model_class.sanitize_input(data)
        
        # Validate using Pydantic
        validated_data = model_class(**sanitized_data)
        
        return validated_data.dict()
        
    except ValidationError as e:
        logger.warning(f"Input validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Input validation failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Input sanitization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input data"
        )


def validate_pagination_params(page: int = 1, page_size: int = ValidationRules.DEFAULT_PAGE_SIZE) -> tuple:
    """Validate pagination parameters."""
    if page < 1:
        page = 1
    
    if page_size < 1:
        page_size = ValidationRules.DEFAULT_PAGE_SIZE
    elif page_size > ValidationRules.MAX_PAGE_SIZE:
        page_size = ValidationRules.MAX_PAGE_SIZE
    
    return page, page_size


def validate_search_query(query: str, max_length: int = 100) -> str:
    """Validate and sanitize search query."""
    if not query:
        return ""
    
    # Sanitize the query
    sanitized = InputSanitizer.sanitize_text(query, max_length)
    
    # Remove SQL injection patterns
    for pattern in InputSanitizer.SQL_INJECTION_PATTERNS:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()


def validate_sort_field(field: str, allowed_fields: List[str]) -> str:
    """Validate sort field against allowed fields."""
    if not field:
        return allowed_fields[0] if allowed_fields else "created_at"
    
    # Remove dangerous characters
    field = re.sub(r'[^a-zA-Z0-9_]', '', field)
    
    if field not in allowed_fields:
        return allowed_fields[0] if allowed_fields else "created_at"
    
    return field


def validate_sort_order(order: str) -> str:
    """Validate sort order."""
    if not order:
        return "desc"
    
    order = order.lower().strip()
    
    if order not in ["asc", "desc"]:
        return "desc"
    
    return order 