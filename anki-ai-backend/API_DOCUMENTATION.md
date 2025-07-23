# Anki-AI Backend API Documentation

## Overview

The Anki-AI Backend API provides a comprehensive spaced repetition flashcard system with AI-powered learning features. This RESTful API is built with FastAPI and provides secure, scalable endpoints for user management, card creation, review scheduling, and learning analytics.

## Base URL

```
https://api.anki-ai.com/api/v1
```

## Authentication

Most endpoints require authentication using JWT tokens. Include your token in the Authorization header:

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

---

## Authentication Endpoints

### Register User

**POST** `/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "username": "johndoe"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "username": "johndoe",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Rate Limit:** 3 requests per hour, 1 per minute burst

### Login User

**POST** `/auth/login`

Authenticate user and receive access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Rate Limit:** 5 requests per 5 minutes, 3 per minute burst

### Get User Profile

**GET** `/auth/profile`

Get current user's profile information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": "johndoe",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Update User Profile

**PUT** `/auth/profile`

Update current user's profile information.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "username": "newusername"
}
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "newemail@example.com",
  "username": "newusername",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Logout User

**POST** `/auth/logout`

Logout current user and invalidate token.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

### Refresh Token

**POST** `/auth/refresh`

Refresh the current access token.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Rate Limit:** 10 requests per 5 minutes, 5 per minute burst

### Request Password Reset

**POST** `/auth/password-reset`

Request a password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset email sent successfully"
}
```

**Rate Limit:** 3 requests per hour, 1 per minute burst

---

## Cards Endpoints

### Create Card

**POST** `/cards/`

Create a new flashcard.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "front": "What is the capital of France?",
  "back": "Paris is the capital and largest city of France.",
  "tags": ["geography", "europe"]
}
```

**Response (201 Created):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "front": "What is the capital of France?",
  "back": "Paris is the capital and largest city of France.",
  "tags": ["geography", "europe"],
  "interval": 1,
  "ease_factor": 2.5,
  "review_count": 0,
  "next_review": "2024-01-01T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Rate Limit:** 20 requests per 5 minutes, 5 per minute burst

### Get Cards

**GET** `/cards/`

Get paginated list of user's cards.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)
- `search` (optional): Search term for card content
- `tags` (optional): Filter by tags (comma-separated)
- `sort_by` (optional): Sort field (created_at, updated_at, next_review)
- `sort_order` (optional): Sort order (asc, desc)

**Response (200 OK):**
```json
{
  "cards": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "front": "What is the capital of France?",
      "back": "Paris is the capital and largest city of France.",
      "tags": ["geography", "europe"],
      "interval": 1,
      "ease_factor": 2.5,
      "review_count": 0,
      "next_review": "2024-01-01T00:00:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

**Rate Limit:** 100 requests per 5 minutes, 20 per minute burst

### Get Card by ID

**GET** `/cards/{card_id}`

Get a specific card by ID.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "front": "What is the capital of France?",
  "back": "Paris is the capital and largest city of France.",
  "tags": ["geography", "europe"],
  "interval": 1,
  "ease_factor": 2.5,
  "review_count": 0,
  "next_review": "2024-01-01T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Rate Limit:** 200 requests per 5 minutes, 50 per minute burst

### Update Card

**PUT** `/cards/{card_id}`

Update a specific card.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "front": "What is the capital of France?",
  "back": "Paris is the capital and largest city of France, known for the Eiffel Tower.",
  "tags": ["geography", "europe", "landmarks"]
}
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "front": "What is the capital of France?",
  "back": "Paris is the capital and largest city of France, known for the Eiffel Tower.",
  "tags": ["geography", "europe", "landmarks"],
  "interval": 1,
  "ease_factor": 2.5,
  "review_count": 0,
  "next_review": "2024-01-01T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Rate Limit:** 30 requests per 5 minutes, 10 per minute burst

### Delete Card

**DELETE** `/cards/{card_id}`

Delete a specific card.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "Card deleted successfully"
}
```

**Rate Limit:** 10 requests per 5 minutes, 3 per minute burst

### Get Due Cards

**GET** `/cards/due/list`

Get list of cards due for review.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)

**Response (200 OK):**
```json
{
  "cards": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "front": "What is the capital of France?",
      "back": "Paris is the capital and largest city of France.",
      "tags": ["geography", "europe"],
      "interval": 1,
      "ease_factor": 2.5,
      "review_count": 0,
      "next_review": "2024-01-01T00:00:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

**Rate Limit:** 100 requests per 5 minutes, 20 per minute burst

### Get Due Count

**GET** `/cards/due/count`

Get count of cards due for review.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "count": 5
}
```

**Rate Limit:** 100 requests per 5 minutes, 20 per minute burst

---

## Reviews Endpoints

### Submit Review

**POST** `/reviews/cards/{card_id}/review`

Submit a review for a card.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "rating": 4
}
```

**Response (200 OK):**
```json
{
  "review": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "card_id": "123e4567-e89b-12d3-a456-426614174000",
    "rating": 4,
    "interval_before": 1,
    "interval_after": 6,
    "ease_factor_before": 2.5,
    "ease_factor_after": 2.6,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "card_updated": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "interval": 6,
    "ease_factor": 2.6,
    "review_count": 1,
    "next_review": "2024-01-07T00:00:00Z"
  },
  "next_review": "2024-01-07T00:00:00Z",
  "message": "Review submitted successfully. Rating: Good. Next review in 6 days."
}
```

**Rate Limit:** 50 requests per 5 minutes, 10 per minute burst

### Get Reviews

**GET** `/reviews/`

Get paginated list of user's reviews.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)
- `card_id` (optional): Filter by card ID
- `rating` (optional): Filter by rating (1-5)
- `sort_by` (optional): Sort field (created_at, rating)
- `sort_order` (optional): Sort order (asc, desc)

**Response (200 OK):**
```json
{
  "reviews": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "card_id": "123e4567-e89b-12d3-a456-426614174000",
      "rating": 4,
      "interval_before": 1,
      "interval_after": 6,
      "ease_factor_before": 2.5,
      "ease_factor_after": 2.6,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

**Rate Limit:** 100 requests per 5 minutes, 20 per minute burst

### Get Card Reviews

**GET** `/reviews/cards/{card_id}`

Get all reviews for a specific card.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)

**Response (200 OK):**
```json
{
  "reviews": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "card_id": "123e4567-e89b-12d3-a456-426614174000",
      "rating": 4,
      "interval_before": 1,
      "interval_after": 6,
      "ease_factor_before": 2.5,
      "ease_factor_after": 2.6,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

**Rate Limit:** 100 requests per 5 minutes, 20 per minute burst

### Get Review Statistics

**GET** `/reviews/stats`

Get learning statistics and analytics.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `period` (optional): Time period (today, week, month, year, all)

**Response (200 OK):**
```json
{
  "total_reviews": 150,
  "reviews_today": 10,
  "reviews_this_week": 45,
  "average_rating": 3.8,
  "cards_studied": 25,
  "due_cards": 5,
  "learning_cards": 3,
  "mature_cards": 22,
  "retention_rate": 0.85,
  "study_streak": 7
}
```

**Rate Limit:** 30 requests per 5 minutes, 10 per minute burst

---

## System Endpoints

### Get Cache Statistics

**GET** `/system/cache/stats`

Get cache performance statistics.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "cache_stats": {
    "hits": 1250,
    "misses": 150,
    "sets": 200,
    "deletes": 50,
    "total_requests": 1400,
    "hit_rate": 89.3,
    "size": 150
  },
  "description": "In-memory cache performance metrics"
}
```

**Rate Limit:** 10 requests per 5 minutes, 3 per minute burst

### Clear Cache

**POST** `/system/cache/clear`

Clear all cached data.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "Cache cleared successfully"
}
```

**Rate Limit:** 2 requests per hour, 1 per minute burst

### Cleanup Expired Cache

**POST** `/system/cache/cleanup`

Remove expired cache entries.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "Cache cleanup completed",
  "removed_items": 25
}
```

**Rate Limit:** 5 requests per hour, 2 per minute burst

---

## Data Models

### User

```json
{
  "id": "string (UUID)",
  "email": "string (email)",
  "username": "string (optional)",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### Card

```json
{
  "id": "string (UUID)",
  "user_id": "string (UUID)",
  "front": "string (1-5000 chars)",
  "back": "string (1-10000 chars)",
  "tags": "array of strings",
  "interval": "integer (days)",
  "ease_factor": "number (1.3-2.5)",
  "review_count": "integer",
  "next_review": "string (ISO 8601)",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### Review

```json
{
  "id": "string (UUID)",
  "user_id": "string (UUID)",
  "card_id": "string (UUID)",
  "rating": "integer (1-5)",
  "interval_before": "integer (days)",
  "interval_after": "integer (days)",
  "ease_factor_before": "number",
  "ease_factor_after": "number",
  "created_at": "string (ISO 8601)"
}
```

### Review Statistics

```json
{
  "total_reviews": "integer",
  "reviews_today": "integer",
  "reviews_this_week": "integer",
  "average_rating": "number",
  "cards_studied": "integer",
  "due_cards": "integer",
  "learning_cards": "integer",
  "mature_cards": "integer",
  "retention_rate": "number (0-1)",
  "study_streak": "integer"
}
```

### Cache Statistics

```json
{
  "hits": "integer",
  "misses": "integer",
  "sets": "integer",
  "deletes": "integer",
  "total_requests": "integer",
  "hit_rate": "number (percentage)",
  "size": "integer"
}
```

---

## Error Responses

### Validation Error (422)

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

### Authentication Error (401)

```json
{
  "detail": "Not authenticated"
}
```

### Authorization Error (403)

```json
{
  "detail": "Not enough permissions"
}
```

### Not Found Error (404)

```json
{
  "detail": "Card not found"
}
```

### Rate Limit Error (429)

```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

### Server Error (500)

```json
{
  "detail": "Internal server error"
}
```

---

## SDK Examples

### Python

```python
import requests

# Base configuration
BASE_URL = "https://api.anki-ai.com/api/v1"
token = "your-jwt-token"
headers = {"Authorization": f"Bearer {token}"}

# Create a card
card_data = {
    "front": "What is Python?",
    "back": "A programming language",
    "tags": ["programming", "python"]
}
response = requests.post(f"{BASE_URL}/cards/", json=card_data, headers=headers)
card = response.json()

# Submit a review
review_data = {"rating": 4}
response = requests.post(f"{BASE_URL}/reviews/cards/{card['id']}/review", 
                        json=review_data, headers=headers)
review = response.json()
```

### JavaScript

```javascript
const BASE_URL = 'https://api.anki-ai.com/api/v1';
const token = 'your-jwt-token';

// Create a card
const cardData = {
  front: 'What is JavaScript?',
  back: 'A programming language',
  tags: ['programming', 'javascript']
};

const response = await fetch(`${BASE_URL}/cards/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(cardData)
});

const card = await response.json();
```

### cURL

```bash
# Register a user
curl -X POST "https://api.anki-ai.com/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "username": "testuser"
  }'

# Login
curl -X POST "https://api.anki-ai.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Create a card (with token)
curl -X POST "https://api.anki-ai.com/api/v1/cards/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "front": "What is the capital of France?",
    "back": "Paris",
    "tags": ["geography"]
  }'
```

---

## Support

For API support and questions:

- **Email**: api-support@anki-ai.com
- **Documentation**: https://docs.anki-ai.com
- **Status Page**: https://status.anki-ai.com
- **GitHub**: https://github.com/anki-ai/backend

---

*This documentation is maintained by the Anki-AI development team. Last updated: January 2024.* 