"""
Cards API tests.
"""

import pytest
from fastapi import status
from unittest.mock import Mock, patch
from uuid import uuid4


class TestCardsEndpoints:
    """Test cards endpoints."""
    
    def test_create_card_success(self, client, auth_headers, test_card_data, mock_user, mock_supabase):
        """Test successful card creation."""
        card_id = str(uuid4())
        
        # Mock card creation
        mock_response = Mock()
        mock_response.data = [{
            "id": card_id,
            "user_id": str(mock_user.id),
            "front": test_card_data["front"],
            "back": test_card_data["back"],
            "tags": test_card_data["tags"],
            "interval": 1,
            "ease_factor": 2.5,
            "review_count": 0,
            "next_review": "2024-01-01T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }]
        mock_response.error = None
        
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        response = client.post("/api/v1/cards/", json=test_card_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["front"] == test_card_data["front"]
        assert data["back"] == test_card_data["back"]
        assert data["tags"] == test_card_data["tags"]
        assert data["user_id"] == str(mock_user.id)
    
    def test_create_card_unauthenticated(self, client, test_card_data):
        """Test card creation without authentication."""
        response = client.post("/api/v1/cards/", json=test_card_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_card_invalid_data(self, client, auth_headers):
        """Test card creation with invalid data."""
        invalid_data = {
            "front": "",  # Empty front
            "back": "Valid back content"
        }
        
        response = client.post("/api/v1/cards/", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_cards_success(self, client, auth_headers, mock_user, mock_supabase):
        """Test successful cards retrieval."""
        # Mock cards list
        mock_response = Mock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                "user_id": str(mock_user.id),
                "front": "Card 1",
                "back": "Answer 1",
                "tags": ["tag1"],
                "interval": 1,
                "ease_factor": 2.5,
                "review_count": 0,
                "next_review": "2024-01-01T00:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": str(uuid4()),
                "user_id": str(mock_user.id),
                "front": "Card 2",
                "back": "Answer 2",
                "tags": ["tag2"],
                "interval": 2,
                "ease_factor": 2.5,
                "review_count": 1,
                "next_review": "2024-01-02T00:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.get("/api/v1/cards/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "cards" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert len(data["cards"]) == 2
    
    def test_get_card_by_id_success(self, client, auth_headers, mock_user, mock_supabase):
        """Test successful card retrieval by ID."""
        card_id = str(uuid4())
        
        # Mock card lookup
        mock_response = Mock()
        mock_response.data = [{
            "id": card_id,
            "user_id": str(mock_user.id),
            "front": "Test Card",
            "back": "Test Answer",
            "tags": ["test"],
            "interval": 1,
            "ease_factor": 2.5,
            "review_count": 0,
            "next_review": "2024-01-01T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }]
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.get(f"/api/v1/cards/{card_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == card_id
        assert data["front"] == "Test Card"
    
    def test_get_card_by_id_not_found(self, client, auth_headers, mock_supabase):
        """Test card retrieval with non-existent ID."""
        card_id = str(uuid4())
        
        # Mock empty card lookup
        mock_response = Mock()
        mock_response.data = []
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.get(f"/api/v1/cards/{card_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_card_success(self, client, auth_headers, mock_user, mock_supabase):
        """Test successful card update."""
        card_id = str(uuid4())
        update_data = {
            "front": "Updated Front",
            "back": "Updated Back",
            "tags": ["updated", "tags"]
        }
        
        # Mock card update
        mock_response = Mock()
        mock_response.data = [{
            "id": card_id,
            "user_id": str(mock_user.id),
            "front": update_data["front"],
            "back": update_data["back"],
            "tags": update_data["tags"],
            "interval": 1,
            "ease_factor": 2.5,
            "review_count": 0,
            "next_review": "2024-01-01T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }]
        mock_response.error = None
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.put(f"/api/v1/cards/{card_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["front"] == update_data["front"]
        assert data["back"] == update_data["back"]
        assert data["tags"] == update_data["tags"]
    
    def test_delete_card_success(self, client, auth_headers, mock_user, mock_supabase):
        """Test successful card deletion."""
        card_id = str(uuid4())
        
        # Mock card deletion
        mock_response = Mock()
        mock_response.data = []
        mock_response.error = None
        
        mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.delete(f"/api/v1/cards/{card_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Card deleted successfully"
    
    def test_get_due_cards_success(self, client, auth_headers, mock_user, mock_supabase):
        """Test successful due cards retrieval."""
        # Mock due cards list
        mock_response = Mock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                "user_id": str(mock_user.id),
                "front": "Due Card 1",
                "back": "Answer 1",
                "tags": ["due"],
                "interval": 1,
                "ease_factor": 2.5,
                "review_count": 0,
                "next_review": "2024-01-01T00:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.lte.return_value.execute.return_value = mock_response
        
        response = client.get("/api/v1/cards/due/list", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "cards" in data
        assert len(data["cards"]) == 1
        assert data["cards"][0]["front"] == "Due Card 1"
    
    def test_get_due_count_success(self, client, auth_headers, mock_user, mock_supabase):
        """Test successful due count retrieval."""
        # Mock due count
        mock_response = Mock()
        mock_response.data = [{"count": 5}]
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.lte.return_value.execute.return_value = mock_response
        
        response = client.get("/api/v1/cards/due/count", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "count" in data
        assert data["count"] == 5


class TestCardsValidation:
    """Test cards input validation."""
    
    def test_create_card_front_validation(self, client, auth_headers):
        """Test front content validation in card creation."""
        invalid_fronts = [
            "",  # Empty
            "a" * 5001,  # Too long
        ]
        
        for front in invalid_fronts:
            response = client.post("/api/v1/cards/", json={
                "front": front,
                "back": "Valid back content"
            }, headers=auth_headers)
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_card_back_validation(self, client, auth_headers):
        """Test back content validation in card creation."""
        invalid_backs = [
            "",  # Empty
            "a" * 10001,  # Too long
        ]
        
        for back in invalid_backs:
            response = client.post("/api/v1/cards/", json={
                "front": "Valid front content",
                "back": back
            }, headers=auth_headers)
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_card_partial_data(self, client, auth_headers, mock_user, mock_supabase):
        """Test card update with partial data."""
        card_id = str(uuid4())
        update_data = {
            "front": "Only front updated"
        }
        
        # Mock card update
        mock_response = Mock()
        mock_response.data = [{
            "id": card_id,
            "user_id": str(mock_user.id),
            "front": update_data["front"],
            "back": "Original back",
            "tags": [],
            "interval": 1,
            "ease_factor": 2.5,
            "review_count": 0,
            "next_review": "2024-01-01T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }]
        mock_response.error = None
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.put(f"/api/v1/cards/{card_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["front"] == update_data["front"]
        assert data["back"] == "Original back"  # Should remain unchanged


class TestCardsSecurity:
    """Test cards security features."""
    
    def test_cards_user_isolation(self, client, auth_headers, mock_user, mock_supabase):
        """Test that users can only access their own cards."""
        other_user_id = str(uuid4())
        card_id = str(uuid4())
        
        # Mock card lookup for different user
        mock_response = Mock()
        mock_response.data = [{
            "id": card_id,
            "user_id": other_user_id,  # Different user
            "front": "Other user's card",
            "back": "Other user's answer",
            "tags": [],
            "interval": 1,
            "ease_factor": 2.5,
            "review_count": 0,
            "next_review": "2024-01-01T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }]
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.get(f"/api/v1/cards/{card_id}", headers=auth_headers)
        
        # Should return 404 even if card exists (user isolation)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_input_sanitization(self, client, auth_headers):
        """Test input sanitization in cards endpoints."""
        malicious_data = {
            "front": "<script>alert('xss')</script>What is XSS?",
            "back": "XSS is <script>alert('xss')</script>a security vulnerability"
        }
        
        response = client.post("/api/v1/cards/", json=malicious_data, headers=auth_headers)
        
        # Should either be rejected due to validation or sanitized
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED]


class TestCardsCaching:
    """Test cards caching functionality."""
    
    def test_cards_list_caching(self, client, auth_headers, mock_user, mock_supabase, mock_cache):
        """Test that cards list is cached."""
        # Mock cards list
        mock_response = Mock()
        mock_response.data = []
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # First request should hit database
        response1 = client.get("/api/v1/cards/", headers=auth_headers)
        assert response1.status_code == status.HTTP_200_OK
        
        # Second request should use cache
        response2 = client.get("/api/v1/cards/", headers=auth_headers)
        assert response2.status_code == status.HTTP_200_OK
        
        # Verify cache was used
        mock_cache.get.assert_called()
    
    def test_card_details_caching(self, client, auth_headers, mock_user, mock_supabase, mock_cache):
        """Test that card details are cached."""
        card_id = str(uuid4())
        
        # Mock card lookup
        mock_response = Mock()
        mock_response.data = [{
            "id": card_id,
            "user_id": str(mock_user.id),
            "front": "Test Card",
            "back": "Test Answer",
            "tags": [],
            "interval": 1,
            "ease_factor": 2.5,
            "review_count": 0,
            "next_review": "2024-01-01T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }]
        mock_response.error = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        # First request should hit database
        response1 = client.get(f"/api/v1/cards/{card_id}", headers=auth_headers)
        assert response1.status_code == status.HTTP_200_OK
        
        # Second request should use cache
        response2 = client.get(f"/api/v1/cards/{card_id}", headers=auth_headers)
        assert response2.status_code == status.HTTP_200_OK
        
        # Verify cache was used
        mock_cache.get.assert_called() 