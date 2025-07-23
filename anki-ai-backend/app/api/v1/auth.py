"""
Authentication API endpoints
Handles user registration, login, and profile management.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from uuid import UUID

from app.core.auth import AuthManager, get_current_user, security
from app.core.supabase import get_supabase
from app.core.logging import logger
from app.models.database import User, UserCreate, UserUpdate

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str = "bearer"
    user: User


class RegisterRequest(BaseModel):
    """Registration request model."""
    email: str
    password: str
    username: Optional[str] = None


class RegisterResponse(BaseModel):
    """Registration response model."""
    access_token: str
    token_type: str = "bearer"
    user: User


class ForgotPasswordRequest(BaseModel):
    """Forgot password request model."""
    email: str


class ResetPasswordRequest(BaseModel):
    """Reset password request model."""
    token: str
    password: str


class PasswordResetResponse(BaseModel):
    """Password reset response model."""
    message: str


class OAuthRequest(BaseModel):
    """OAuth request model."""
    provider: str  # "google" or "github"
    code: str
    redirect_uri: str


class OAuthResponse(BaseModel):
    """OAuth response model."""
    access_token: str
    token_type: str = "bearer"
    user: User
    is_new_user: bool = False


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """Register a new user."""
    try:
        supabase = get_supabase()
        
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user account"
            )
        
        user_id = auth_response.user.id
        
        # Create user profile in our database
        user = await AuthManager.create_user_profile(
            user_id=user_id,
            email=request.email,
            username=request.username
        )
        
        # Create access token
        access_token = AuthManager.create_access_token(
            data={"user_id": str(user_id)}
        )
        
        logger.info(f"User registered successfully: {user.email}")
        
        return RegisterResponse(
            access_token=access_token,
            user=user
        )
        
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login with email and password."""
    try:
        supabase = get_supabase()
        
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        user_id = auth_response.user.id
        
        # Get user profile from our database
        user = await AuthManager.get_user_by_id(user_id)
        
        # Create access token
        access_token = AuthManager.create_access_token(
            data={"user_id": str(user_id)}
        )
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return LoginResponse(
            access_token=access_token,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout the current user."""
    try:
        supabase = get_supabase()
        supabase.auth.sign_out()
        
        logger.info("User logged out successfully")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me", response_model=User)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get the current user's profile."""
    return current_user

@router.get("/me-by-id/{user_id}", response_model=User)
async def get_user_profile_by_id(user_id: str):
    """Get user profile by Supabase user ID."""
    try:
        user_uuid = UUID(user_id)
        return await AuthManager.get_user_by_id(user_uuid)
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

class CreateProfileRequest(BaseModel):
    """Create profile request model."""
    user_id: str
    email: str
    username: Optional[str] = None

@router.post("/create-profile", response_model=User)
async def create_user_profile(request: CreateProfileRequest):
    """Create a user profile in the backend database."""
    try:
        user_uuid = UUID(request.user_id)
        
        # Check if user already exists
        try:
            existing_user = await AuthManager.get_user_by_id(user_uuid)
            return existing_user
        except HTTPException:
            # User doesn't exist, create new profile
            pass
        
        # Create new user profile
        user = await AuthManager.create_user_profile(
            user_id=user_uuid,
            email=request.email,
            username=request.username or request.email.split('@')[0]
        )
        
        logger.info(f"Created user profile for {request.email}")
        return user
        
    except Exception as e:
        logger.error(f"Error creating user profile for {request.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user profile"
        )

@router.post("/validate-supabase-token", response_model=User)
async def validate_supabase_token(token: str):
    """Validate a Supabase token and return user data."""
    try:
        supabase = get_supabase()
        user_data = supabase.auth.get_user(token)
        user_id = UUID(user_data.user.id)
        return await AuthManager.get_user_by_id(user_id)
    except Exception as e:
        logger.error(f"Supabase token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/debug-token")
async def debug_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Debug endpoint to see what token is being received."""
    token = credentials.credentials
    logger.info(f"Received token: {token[:20]}...")
    
    try:
        # Try to decode the token to see what it contains
        import jwt
        decoded = jwt.decode(token, options={"verify_signature": False})
        logger.info(f"Token payload: {decoded}")
        
        # Try Supabase validation
        supabase = get_supabase()
        user_data = supabase.auth.get_user(token)
        logger.info(f"Supabase user data: {user_data}")
        
        return {
            "token_received": True,
            "token_preview": token[:20] + "...",
            "decoded_payload": decoded,
            "supabase_validation": "success"
        }
    except Exception as e:
        logger.error(f"Token debug error: {e}")
        return {
            "token_received": True,
            "token_preview": token[:20] + "...",
            "error": str(e)
        }


@router.put("/me", response_model=User)
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update the current user's profile."""
    try:
        # Filter out None values
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )
        
        updated_user = await AuthManager.update_user_profile(
            user_id=current_user.id,
            update_data=update_dict
        )
        
        logger.info(f"User profile updated: {current_user.email}")
        
        return updated_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh the access token."""
    try:
        # Verify current token
        payload = AuthManager.verify_token(credentials.credentials)
        if not payload or "user_id" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Create new token
        new_token = AuthManager.create_access_token(
            data={"user_id": payload["user_id"]}
        )
        
        logger.info("Token refreshed successfully")
        
        return {
            "access_token": new_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


@router.post("/forgot-password", response_model=PasswordResetResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset email."""
    try:
        supabase = get_supabase()
        
        # Send password reset email via Supabase Auth
        response = supabase.auth.reset_password_email(request.email)
        
        logger.info(f"Password reset email sent to: {request.email}")
        
        return PasswordResetResponse(
            message="Password reset email sent successfully. Please check your email."
        )
        
    except Exception as e:
        logger.error(f"Password reset email failed: {e}")
        # Don't expose whether the email exists or not for security
        return PasswordResetResponse(
            message="If the email exists, a password reset link has been sent."
        )


@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(request: ResetPasswordRequest):
    """Reset password using token from email."""
    try:
        supabase = get_supabase()
        
        # Update password using the reset token
        response = supabase.auth.update_user({
            "password": request.password
        })
        
        logger.info("Password reset completed successfully")
        
        return PasswordResetResponse(
            message="Password reset successfully. You can now login with your new password."
        )
        
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token. Please request a new password reset."
        )


@router.post("/change-password", response_model=PasswordResetResponse)
async def change_password(
    request: ResetPasswordRequest,
    current_user: User = Depends(get_current_user)
):
    """Change password for authenticated user."""
    try:
        supabase = get_supabase()
        
        # Update password for the current user
        response = supabase.auth.update_user({
            "password": request.password
        })
        
        logger.info(f"Password changed successfully for user: {current_user.email}")
        
        return PasswordResetResponse(
            message="Password changed successfully."
        )
        
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post("/oauth", response_model=OAuthResponse)
async def oauth_login(request: OAuthRequest):
    """Handle OAuth login with Google or GitHub."""
    try:
        supabase = get_supabase()
        
        # Exchange code for session
        auth_response = supabase.auth.exchange_code_for_session(request.code)
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OAuth code"
            )
        
        user_id = auth_response.user.id
        email = auth_response.user.email
        user_metadata = auth_response.user.user_metadata or {}
        
        # Check if user profile exists
        try:
            user = await AuthManager.get_user_by_id(user_id)
            is_new_user = False
        except HTTPException:
            # User doesn't exist, create profile
            username = user_metadata.get('name') or user_metadata.get('login') or email.split('@')[0]
            user = await AuthManager.create_user_profile(
                user_id=user_id,
                email=email,
                username=username
            )
            is_new_user = True
        
        # Create access token
        access_token = AuthManager.create_access_token(
            data={"user_id": str(user_id)}
        )
        
        logger.info(f"OAuth login successful: {user.email} (provider: {request.provider})")
        
        return OAuthResponse(
            access_token=access_token,
            user=user,
            is_new_user=is_new_user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth login failed"
        )


@router.get("/oauth/{provider}/url")
async def get_oauth_url(provider: str):
    """Get OAuth URL for the specified provider."""
    try:
        supabase = get_supabase()
        
        # Generate a random state parameter for security
        import secrets
        state = secrets.token_urlsafe(32)
        
        if provider == "google":
            # For Google OAuth, we need to redirect to Supabase's OAuth endpoint
            # with proper state parameter and redirect URL
            # Note: Supabase will handle the OAuth flow and redirect back to our callback
            # The redirect_to should match the authorized redirect URI in Google OAuth
            # Use the site URL as the redirect target for better compatibility
            oauth_url = f"{supabase.supabase_url}/auth/v1/authorize?provider=google&redirect_to=http://localhost:3000&state={state}"
            return {"url": oauth_url, "state": state}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {provider}"
            )
        
    except Exception as e:
        logger.error(f"Failed to get OAuth URL for {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get OAuth URL for {provider}"
        ) 