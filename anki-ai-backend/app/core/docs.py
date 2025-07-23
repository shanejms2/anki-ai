"""
API Documentation Configuration
Provides detailed OpenAPI/Swagger documentation with examples and schemas.
"""

from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from app.core.config import settings


def custom_openapi(app: FastAPI):
    """Generate custom OpenAPI schema with detailed documentation."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description="""
# Anki-AI Backend API

A comprehensive spaced repetition flashcard system with AI-powered learning features.

## Features

- **User Authentication**: Secure JWT-based authentication with password reset
- **Card Management**: Create, update, and organize flashcards with tags
- **Spaced Repetition**: SM-2 algorithm for optimal review scheduling
- **Review System**: Track learning progress and performance statistics
- **Caching**: High-performance in-memory caching for frequently accessed data
- **Security**: Rate limiting, input validation, and comprehensive security measures

## Authentication

All API endpoints require authentication except for registration and login. Include your JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Rate limit information is included in response headers:

- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Timestamp when limit resets

## Error Handling

The API returns standard HTTP status codes and detailed error messages:

- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Security

- All user input is sanitized and validated
- SQL injection and XSS protection
- Row-level security ensures data isolation
- Comprehensive logging and monitoring
        """,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token for authentication"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # Add detailed examples
    openapi_schema["components"]["examples"] = {
        "UserRegistration": {
            "summary": "User Registration Example",
            "value": {
                "email": "user@example.com",
                "password": "securepassword123",
                "username": "johndoe"
            }
        },
        "UserLogin": {
            "summary": "User Login Example",
            "value": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        },
        "CardCreation": {
            "summary": "Card Creation Example",
            "value": {
                "front": "What is the capital of France?",
                "back": "Paris is the capital and largest city of France.",
                "tags": ["geography", "europe"]
            }
        },
        "CardUpdate": {
            "summary": "Card Update Example",
            "value": {
                "front": "What is the capital of France?",
                "back": "Paris is the capital and largest city of France, known for the Eiffel Tower.",
                "tags": ["geography", "europe", "landmarks"]
            }
        },
        "ReviewSubmission": {
            "summary": "Review Submission Example",
            "value": {
                "rating": 4,
                "card_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        },
        "ErrorResponse": {
            "summary": "Error Response Example",
            "value": {
                "detail": "Validation error occurred",
                "errors": [
                    {
                        "field": "email",
                        "message": "Invalid email format"
                    }
                ]
            }
        }
    }
    
    # Add detailed schemas
    openapi_schema["components"]["schemas"].update({
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid", "description": "User's unique identifier"},
                "email": {"type": "string", "format": "email", "description": "User's email address"},
                "username": {"type": "string", "description": "User's username"},
                "created_at": {"type": "string", "format": "date-time", "description": "Account creation timestamp"},
                "updated_at": {"type": "string", "format": "date-time", "description": "Last update timestamp"}
            },
            "required": ["id", "email", "created_at", "updated_at"]
        },
        "Card": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid", "description": "Card's unique identifier"},
                "user_id": {"type": "string", "format": "uuid", "description": "Owner user's ID"},
                "front": {"type": "string", "description": "Card front content"},
                "back": {"type": "string", "description": "Card back content"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Card tags"},
                "interval": {"type": "integer", "description": "Current review interval in days"},
                "ease_factor": {"type": "number", "description": "Current ease factor"},
                "review_count": {"type": "integer", "description": "Number of reviews completed"},
                "next_review": {"type": "string", "format": "date-time", "description": "Next review date"},
                "created_at": {"type": "string", "format": "date-time", "description": "Creation timestamp"},
                "updated_at": {"type": "string", "format": "date-time", "description": "Last update timestamp"}
            },
            "required": ["id", "user_id", "front", "back", "interval", "ease_factor", "review_count", "created_at", "updated_at"]
        },
        "Review": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid", "description": "Review's unique identifier"},
                "user_id": {"type": "string", "format": "uuid", "description": "User who submitted the review"},
                "card_id": {"type": "string", "format": "uuid", "description": "Reviewed card's ID"},
                "rating": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Review rating (1-5)"},
                "interval_before": {"type": "integer", "description": "Interval before review"},
                "interval_after": {"type": "integer", "description": "Interval after review"},
                "ease_factor_before": {"type": "number", "description": "Ease factor before review"},
                "ease_factor_after": {"type": "number", "description": "Ease factor after review"},
                "created_at": {"type": "string", "format": "date-time", "description": "Review timestamp"}
            },
            "required": ["id", "user_id", "card_id", "rating", "interval_before", "interval_after", "ease_factor_before", "ease_factor_after", "created_at"]
        },
        "ReviewStats": {
            "type": "object",
            "properties": {
                "total_reviews": {"type": "integer", "description": "Total number of reviews"},
                "reviews_today": {"type": "integer", "description": "Reviews completed today"},
                "reviews_this_week": {"type": "integer", "description": "Reviews completed this week"},
                "average_rating": {"type": "number", "description": "Average review rating"},
                "cards_studied": {"type": "integer", "description": "Number of unique cards studied"},
                "due_cards": {"type": "integer", "description": "Number of cards due for review"},
                "learning_cards": {"type": "integer", "description": "Number of cards in learning phase"},
                "mature_cards": {"type": "integer", "description": "Number of mature cards"}
            }
        },
        "CacheStats": {
            "type": "object",
            "properties": {
                "hits": {"type": "integer", "description": "Number of cache hits"},
                "misses": {"type": "integer", "description": "Number of cache misses"},
                "sets": {"type": "integer", "description": "Number of cache sets"},
                "deletes": {"type": "integer", "description": "Number of cache deletions"},
                "total_requests": {"type": "integer", "description": "Total cache requests"},
                "hit_rate": {"type": "number", "description": "Cache hit rate percentage"},
                "size": {"type": "integer", "description": "Current cache size"}
            }
        }
    })
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def setup_documentation(app: FastAPI):
    """Setup API documentation with custom schema."""
    app.openapi = lambda: custom_openapi(app) 