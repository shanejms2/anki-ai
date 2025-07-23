"""
Authentication and Authorization Module
Handles JWT token validation, user authentication, and authorization.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from uuid import UUID
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.supabase import get_supabase
from app.core.logging import logger
from app.models.database import User

# Security scheme for JWT tokens
security = HTTPBearer()


class AuthManager:
    """Manages authentication and authorization."""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"JWT token verification failed: {e}")
            return None
    
    @staticmethod
    async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        logger.info("=== ENTERED get_current_user ===")
        token = credentials.credentials
        logger.info(f"Token received: {token[:20]}...")
        # First try to verify with our JWT secret
        logger.info("Step 1: Verifying token with JWT secret (before)")
        payload = AuthManager.verify_token(token)
        logger.info("Step 1: Verifying token with JWT secret (after)")
        if payload and "user_id" in payload:
            logger.info("Token validated with JWT secret")
            user_id = UUID(payload["user_id"])
            logger.info("Step 2: Getting user by ID from DB (before)")
            user = await AuthManager.get_user_by_id(user_id)
            logger.info("Step 2: Getting user by ID from DB (after)")
            return user
        # If that fails, try to verify with Supabase
        try:
            logger.info("Step 3: Attempting Supabase token validation (before)")
            supabase = get_supabase()
            logger.info("Step 3: Supabase client retrieved (after)")
            user_data = await run_in_threadpool(lambda: supabase.auth.get_user(token))
            logger.info(f"Step 3: Supabase token validation successful for user: {user_data.user.id} (after)")
            user_id = UUID(user_data.user.id)
            # Try to get user from database
            try:
                logger.info("Step 4: Getting user by ID from DB (before)")
                user = await AuthManager.get_user_by_id(user_id)
                logger.info("Step 4: Getting user by ID from DB (after)")
                return user
            except HTTPException as user_error:
                if user_error.status_code == 404:
                    logger.info(f"User {user_id} not found in database, creating from Supabase data (before)")
                    user = await AuthManager.create_user_from_supabase(user_data.user)
                    logger.info(f"User {user_id} created from Supabase data (after)")
                    return user
                else:
                    logger.error(f"HTTPException in get_user_by_id: {user_error}")
                    raise user_error
        except Exception as e:
            logger.warning(f"Supabase token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def get_user_by_id(user_id: UUID) -> User:
        """Get a user by their ID."""
        try:
            supabase = get_supabase()
            response = await run_in_threadpool(lambda: supabase.table("users").select("*").eq("id", str(user_id)).execute())
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user_data = response.data[0]
            return User(**user_data)
            
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching user data"
            )
    
    @staticmethod
    async def create_user_from_supabase(supabase_user) -> User:
        """Create a user in the database from Supabase user data."""
        try:
            supabase = get_supabase()
            
            # Extract user data from Supabase user
            user_data = {
                "id": supabase_user.id,
                "email": supabase_user.email,
                "username": supabase_user.user_metadata.get("username", supabase_user.email.split("@")[0]) if supabase_user.email else "user",
                "created_at": supabase_user.created_at,
                "updated_at": supabase_user.last_sign_in_at or supabase_user.created_at
            }
            
            # Insert user into database
            response = await run_in_threadpool(lambda: supabase.table("users").insert(user_data).execute())
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user profile"
                )
            
            logger.info(f"Created user profile for {user_data['email']}")
            return User(**response.data[0])
            
        except Exception as e:
            logger.error(f"Error creating user from Supabase: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user profile"
            )
    
    @staticmethod
    async def create_user_profile(user_id: UUID, email: str, username: Optional[str] = None) -> User:
        """Create a user profile in our database."""
        try:
            supabase = get_supabase()
            user_data = {
                "id": str(user_id),
                "email": email,
                "username": username
            }
            
            response = await run_in_threadpool(lambda: supabase.table("users").insert(user_data).execute())
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user profile"
                )
            
            return User(**response.data[0])
            
        except Exception as e:
            logger.error(f"Error creating user profile for {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user profile"
            )
    
    @staticmethod
    async def update_user_profile(user_id: UUID, update_data: dict) -> User:
        """Update a user's profile."""
        try:
            supabase = get_supabase()
            response = await run_in_threadpool(lambda: supabase.table("users").update(update_data).eq("id", str(user_id)).execute())
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return User(**response.data[0])
            
        except Exception as e:
            logger.error(f"Error updating user profile for {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating user profile"
            )


# Dependency for getting current user
async def get_current_user(user: User = Depends(AuthManager.get_current_user)) -> User:
    """Dependency to get the current authenticated user."""
    return user


# Dependency for optional authentication (for public endpoints)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Get the current user if authenticated, otherwise return None."""
    if not credentials:
        return None
    
    try:
        return await AuthManager.get_current_user(credentials)
    except HTTPException:
        return None 