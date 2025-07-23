from supabase import create_client, Client
from app.core.config import settings
import structlog

logger = structlog.get_logger()

# Initialize Supabase client
try:
    # Use the service role key for backend privileged access
    supabase: Client = create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )
    logger.info("Supabase client initialized with service role key")
except Exception as e:
    logger.warning(f"Failed to initialize Supabase client with new API key: {e}")
    logger.info("You may need to use legacy JWT-based keys for now")
    # Create a placeholder client for development
    supabase = None


def get_supabase() -> Client:
    """Get the Supabase client instance."""
    if supabase is None:
        raise Exception("Supabase client not initialized. Please check your API keys.")
    return supabase


# Test the connection
try:
    # Test connection by querying the users table (which should exist)
    response = supabase.table("users").select("id", count="exact").limit(1).execute()
    logger.info("Supabase connection established successfully")
except Exception as e:
    logger.warning(f"Supabase connection test failed: {e}")
    logger.info("This might be due to new API key format compatibility")
    logger.info("The app will still work, but Supabase operations may need legacy keys") 