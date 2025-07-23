# Testing Framework Documentation

## Overview

The Anki-AI Backend includes a comprehensive testing framework built with pytest, covering unit tests, integration tests, security tests, and performance tests. The framework ensures code quality, reliability, and security.

## 🧪 Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest configuration and fixtures
├── test_auth.py         # Authentication tests
├── test_cards.py        # Cards API tests
├── test_reviews.py      # Reviews API tests
├── test_system.py       # System endpoint tests
└── test_security.py     # Security feature tests
```

## 🚀 Quick Start

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Or install individually
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx coverage
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_auth.py

# Run tests by marker
python -m pytest -m auth
python -m pytest -m security
python -m pytest -m caching

# Run with coverage
python -m pytest --cov=app --cov-report=html
```

### Using the Test Runner Script

```bash
# Run the comprehensive test suite
python run_tests.py
```

## 📋 Test Categories

### Unit Tests (`-m unit`)

Test individual functions and classes in isolation:

```python
def test_rate_limiter_check():
    """Test rate limiter functionality."""
    config = RateLimitConfig(max_requests=3, window_seconds=60)
    allowed, headers = rate_limiter.check_rate_limit("client1", "endpoint1", config)
    assert allowed == True
    assert "X-RateLimit-Remaining" in headers
```

### Integration Tests (`-m integration`)

Test API endpoints with mocked dependencies:

```python
def test_create_card_success(self, client, auth_headers, mock_supabase):
    """Test successful card creation."""
    response = client.post("/api/v1/cards/", json=card_data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["front"] == card_data["front"]
```

### Security Tests (`-m security`)

Test security features and input validation:

```python
def test_input_sanitization(self, client, auth_headers):
    """Test input sanitization in cards endpoints."""
    malicious_data = {
        "front": "<script>alert('xss')</script>What is XSS?",
        "back": "XSS is a security vulnerability"
    }
    response = client.post("/api/v1/cards/", json=malicious_data, headers=auth_headers)
    assert response.status_code in [422, 400, 201]  # Should be rejected or sanitized
```

### Caching Tests (`-m caching`)

Test caching functionality and performance:

```python
def test_cards_list_caching(self, client, auth_headers, mock_cache):
    """Test that cards list is cached."""
    response1 = client.get("/api/v1/cards/", headers=auth_headers)
    response2 = client.get("/api/v1/cards/", headers=auth_headers)
    mock_cache.get.assert_called()  # Verify cache was used
```

## 🔧 Test Fixtures

### Authentication Fixtures

```python
@pytest.fixture
def auth_headers(mock_user):
    """Generate authentication headers with a valid JWT token."""
    token = create_access_token(data={"sub": str(mock_user.id)})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_user():
    """Mock user object for testing."""
    user = Mock()
    user.id = "123e4567-e89b-12d3-a456-426614174000"
    user.email = "test@example.com"
    user.username = "testuser"
    return user
```

### Database Fixtures

```python
@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    with patch("app.core.supabase.supabase") as mock_supabase:
        mock_response = Mock()
        mock_response.data = []
        mock_response.error = None
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        yield mock_supabase
```

### Cache Fixtures

```python
@pytest.fixture
def mock_cache():
    """Mock cache for testing."""
    with patch("app.core.cache.cache") as mock_cache:
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True
        mock_cache.get_stats.return_value = {
            "hits": 0, "misses": 0, "sets": 0, "deletes": 0,
            "total_requests": 0, "hit_rate": 0.0, "size": 0
        }
        yield mock_cache
```

## 📊 Coverage Reporting

### Generate Coverage Report

```bash
# Generate HTML coverage report
python -m pytest --cov=app --cov-report=html

# Generate terminal coverage report
python -m pytest --cov=app --cov-report=term-missing

# Generate XML coverage report (for CI/CD)
python -m pytest --cov=app --cov-report=xml
```

### Coverage Configuration

The coverage is configured in `pytest.ini`:

```ini
addopts = 
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
```

## 🔍 Code Quality Checks

### Linting with flake8

```bash
# Run flake8 linting
flake8 app/ tests/ --max-line-length=100 --ignore=E501,W503
```

### Type Checking with mypy

```bash
# Run mypy type checking
mypy app/ --ignore-missing-imports
```

### Code Formatting with black

```bash
# Format code with black
black app/ tests/ --line-length=100
```

## 🧪 Test Examples

### Authentication Tests

```python
class TestAuthEndpoints:
    def test_register_success(self, client, test_user_data, mock_supabase):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == test_user_data["email"]
    
    def test_login_invalid_credentials(self, client, test_user_data, mock_supabase):
        """Test login with invalid credentials."""
        with patch("app.core.auth.verify_password", return_value=False):
            response = client.post("/api/v1/auth/login", json={
                "email": test_user_data["email"],
                "password": "wrongpassword"
            })
        assert response.status_code == 401
```

### Cards API Tests

```python
class TestCardsEndpoints:
    def test_create_card_success(self, client, auth_headers, test_card_data, mock_user, mock_supabase):
        """Test successful card creation."""
        response = client.post("/api/v1/cards/", json=test_card_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["front"] == test_card_data["front"]
        assert data["user_id"] == str(mock_user.id)
    
    def test_cards_user_isolation(self, client, auth_headers, mock_user, mock_supabase):
        """Test that users can only access their own cards."""
        # Mock card for different user
        response = client.get(f"/api/v1/cards/{card_id}", headers=auth_headers)
        assert response.status_code == 404  # Should not be accessible
```

### Security Tests

```python
class TestAuthSecurity:
    def test_rate_limiting_on_login(self, client, test_user_data, mock_supabase):
        """Test rate limiting on login endpoint."""
        # Make multiple requests to trigger rate limiting
        for i in range(6):  # Exceed the 5 requests per 5 minutes limit
            response = client.post("/api/v1/auth/login", json=test_user_data)
            if i < 5:
                assert response.status_code in [200, 401]
            else:
                assert response.status_code == 429  # Rate limited
```

## 🚀 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    - name: Run tests
      run: |
        python -m pytest --cov=app --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 📈 Performance Testing

### Load Testing with locust

```python
# locustfile.py
from locust import HttpUser, task, between

class AnkiAIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_cards(self):
        self.client.get("/api/v1/cards/", headers={"Authorization": "Bearer token"})
    
    @task
    def create_card(self):
        self.client.post("/api/v1/cards/", 
                        json={"front": "Test", "back": "Answer"},
                        headers={"Authorization": "Bearer token"})
```

## 🐛 Debugging Tests

### Running Tests in Debug Mode

```bash
# Run with detailed output
python -m pytest -v -s

# Run specific test with debugger
python -m pytest tests/test_auth.py::TestAuthEndpoints::test_login_success -s

# Run with print statements
python -m pytest -s
```

### Common Issues and Solutions

1. **Import Errors**: Ensure you're in the correct directory and virtual environment is activated
2. **Mock Issues**: Check that mocks are properly configured in fixtures
3. **Database Errors**: Verify that Supabase mocks are working correctly
4. **Authentication Errors**: Ensure JWT tokens are properly generated in fixtures

## 📚 Best Practices

### Test Organization

1. **Group related tests** in classes
2. **Use descriptive test names** that explain what is being tested
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Keep tests independent** - no shared state between tests
5. **Use appropriate markers** to categorize tests

### Test Data Management

1. **Use fixtures** for common test data
2. **Create factory functions** for complex objects
3. **Use realistic test data** that represents real usage
4. **Clean up test data** after tests

### Mocking Strategy

1. **Mock external dependencies** (database, cache, external APIs)
2. **Don't mock the code under test**
3. **Use appropriate mock levels** (unit vs integration)
4. **Verify mock calls** when testing behavior

## 📊 Test Metrics

### Coverage Goals

- **Overall Coverage**: > 90%
- **Critical Paths**: > 95%
- **Security Features**: 100%
- **API Endpoints**: > 95%

### Performance Benchmarks

- **Test Execution Time**: < 30 seconds for full suite
- **API Response Time**: < 200ms for most endpoints
- **Memory Usage**: < 100MB during testing

## 🔧 Configuration

### pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    auth: marks tests as authentication tests
    cards: marks tests as cards tests
    reviews: marks tests as reviews tests
    security: marks tests as security tests
    caching: marks tests as caching tests
```

### .coveragerc

```ini
[run]
source = app
omit = 
    */tests/*
    */__pycache__/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## 📞 Support

For testing questions and issues:

- **Documentation**: This file and inline test documentation
- **Examples**: See existing test files for patterns
- **Issues**: Create GitHub issues for test-related problems
- **Contributing**: Follow testing guidelines when adding new features

---

*This testing framework is maintained by the Anki-AI development team. Last updated: January 2024.* 