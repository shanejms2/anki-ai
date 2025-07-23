"""
Authentication API tests.
"""

import pytest
from fastapi import status
from unittest.mock import Mock, patch


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_register_success(self, client, test_user_data, mock_supabase):
        """Test successful user registration."""
        # Mock successful user creation
        mock_response = Mock()
        mock_response.data = [{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": test_user_data["email"],
            "username": test_user_data["username"],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }]
        mock_response.error = None
        
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "user" in data
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user_data["email"]
    
    def test_register_duplicate_email(self, client, test_user_data, mock_supabase):
        """Test registration with duplicate email."""
        # Mock duplicate email error
        mock_response = Mock()
        mock_response.data = None
        mock_response.error = {"message": "duplicate key value violates unique constraint"}
        
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_data(self, client):
        """Test registration with invalid data."""
        invalid_data = {
            "email": "invalid-email",
            "password": "123",  # Too short
            "username": "ab"  # Too short
        }
        
        response = client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_success(self, client, test_user_data, mock_supabase):
        """Test successful user login."""
        # Mock user lookup
        mock_response = Mock()
        mock_response.data = [{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": test_user_data["email"],
            "password_hash": "$2b$12$hashedpassword",  # Mocked hash
            "username": test_user_data["username"]
        }]
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Mock password verification
        with patch("app.core.auth.verify_password", return_value=True):
            response = client.post("/api/v1/auth/login", json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client, test_user_data, mock_supabase):
        """Test login with invalid credentials."""
        # Mock user lookup
        mock_response = Mock()
        mock_response.data = [{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": test_user_data["email"],
            "password_hash": "$2b$12$hashedpassword",
            "username": test_user_data["username"]
        }]
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Mock password verification failure
        with patch("app.core.auth.verify_password", return_value=False):
            response = client.post("/api/v1/auth/login", json={
                "email": test_user_data["email"],
                "password": "wrongpassword"
            })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid credentials" in response.json()["detail"].lower()
    
    def test_login_user_not_found(self, client, test_user_data, mock_supabase):
        """Test login with non-existent user."""
        # Mock empty user lookup
        mock_response = Mock()
        mock_response.data = []
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid credentials" in response.json()["detail"].lower()
    
    def test_get_profile_authenticated(self, client, auth_headers, mock_user, mock_supabase):
        """Test getting user profile with valid authentication."""
        # Mock user lookup
        mock_response = Mock()
        mock_response.data = [{
            "id": str(mock_user.id),
            "email": mock_user.email,
            "username": mock_user.username,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }]
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.get("/api/v1/auth/profile", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == mock_user.email
        assert data["username"] == mock_user.username
    
    def test_get_profile_unauthenticated(self, client):
        """Test getting user profile without authentication."""
        response = client.get("/api/v1/auth/profile")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile_success(self, client, auth_headers, mock_user, mock_supabase):
        """Test successful profile update."""
        update_data = {
            "username": "newusername",
            "email": "newemail@example.com"
        }
        
        # Mock user update
        mock_response = Mock()
        mock_response.data = [{
            "id": str(mock_user.id),
            "email": update_data["email"],
            "username": update_data["username"],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }]
        mock_response.error = None
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.put("/api/v1/auth/profile", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == update_data["email"]
        assert data["username"] == update_data["username"]
    
    def test_logout_success(self, client, auth_headers):
        """Test successful logout."""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Successfully logged out"
    
    def test_refresh_token_success(self, client, auth_headers, mock_user):
        """Test successful token refresh."""
        response = client.post("/api/v1/auth/refresh", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_password_reset_request(self, client, test_user_data, mock_supabase):
        """Test password reset request."""
        # Mock user lookup
        mock_response = Mock()
        mock_response.data = [{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": test_user_data["email"]
        }]
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Mock password reset email
        with patch("app.core.auth.send_password_reset_email", return_value=True):
            response = client.post("/api/v1/auth/password-reset", json={
                "email": test_user_data["email"]
            })
        
        assert response.status_code == status.HTTP_200_OK
        assert "password reset email sent" in response.json()["message"].lower()


class TestAuthValidation:
    """Test authentication input validation."""
    
    def test_register_email_validation(self, client):
        """Test email validation in registration."""
        invalid_emails = [
            "invalid-email",
            "test@",
            "@example.com",
            "test..test@example.com"
        ]
        
        for email in invalid_emails:
            response = client.post("/api/v1/auth/register", json={
                "email": email,
                "password": "validpassword123",
                "username": "testuser"
            })
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_password_validation(self, client):
        """Test password validation in registration."""
        invalid_passwords = [
            "123",  # Too short
            "a" * 129,  # Too long
            "",  # Empty
        ]
        
        for password in invalid_passwords:
            response = client.post("/api/v1/auth/register", json={
                "email": "test@example.com",
                "password": password,
                "username": "testuser"
            })
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_username_validation(self, client):
        """Test username validation in registration."""
        invalid_usernames = [
            "ab",  # Too short
            "a" * 51,  # Too long
            "",  # Empty
        ]
        
        for username in invalid_usernames:
            response = client.post("/api/v1/auth/register", json={
                "email": "test@example.com",
                "password": "validpassword123",
                "username": username
            })
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthSecurity:
    """Test authentication security features."""
    
    def test_rate_limiting_on_login(self, client, test_user_data, mock_supabase):
        """Test rate limiting on login endpoint."""
        # Mock user lookup
        mock_response = Mock()
        mock_response.data = [{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": test_user_data["email"],
            "password_hash": "$2b$12$hashedpassword",
            "username": test_user_data["username"]
        }]
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Mock password verification
        with patch("app.core.auth.verify_password", return_value=True):
            # Make multiple requests to trigger rate limiting
            for i in range(6):  # Exceed the 5 requests per 5 minutes limit
                response = client.post("/api/v1/auth/login", json={
                    "email": test_user_data["email"],
                    "password": test_user_data["password"]
                })
                
                if i < 5:
                    assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
                else:
                    # The 6th request should be rate limited
                    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    
    def test_input_sanitization(self, client):
        """Test input sanitization in authentication endpoints."""
        malicious_data = {
            "email": "test@example.com<script>alert('xss')</script>",
            "password": "password123",
            "username": "user<script>alert('xss')</script>"
        }
        
        response = client.post("/api/v1/auth/register", json=malicious_data)
        
        # Should either be rejected due to validation or sanitized
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST] 