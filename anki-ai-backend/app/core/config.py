from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Application Configuration
    app_name: str = "Anki-AI Backend"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    
    # Supabase Configuration
    supabase_url: str
    supabase_service_role_key: str  # Use the service role key for backend privileged access
    
    # JWT Configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS Configuration
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # OAuth Configuration
    google_client_id: str = ""
    google_client_secret: str = ""
    
    # Logging Configuration
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 