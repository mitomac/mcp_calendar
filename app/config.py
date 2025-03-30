"""
Configuration settings for the Duke Calendar MCP Server
"""

import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    """Application settings"""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]  # For development - restrict in production
    
    # Duke Calendar API
    DUKE_CALENDAR_API_URL: str = os.getenv(
        "DUKE_CALENDAR_API_URL", 
        "https://calendar.duke.edu/events/index.json"
    )
    
    # Debug mode
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Reference data cache time (in seconds)
    REFERENCE_CACHE_TTL: int = int(os.getenv("REFERENCE_CACHE_TTL", "3600"))  # 1 hour
    
    model_config = {
        "case_sensitive": True
    }

# Initialize settings
settings = Settings()
