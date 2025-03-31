"""
Configuration settings for the Duke MCP Server
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

# Get the directory where config.py is located (app directory)
CURRENT_DIR = Path(__file__).resolve().parent
# Go up one directory to the project root where .env should be
BASE_DIR = CURRENT_DIR.parent

# Load .env file from the project root
load_dotenv(os.path.join(BASE_DIR, '.env'))



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
    
    # Duke Directory API
    DUKE_DIRECTORY_API_KEY: str = os.getenv(
        "DUKE_DIRECTORY_API_KEY"
    )
    
    DUKE_DIRECTORY_BASE_URL: str = os.getenv(
        "DUKE_DIRECTORY_BASE_URL",
        "https://streamer.oit.duke.edu/ldap/people"
    )
    
    # Duke Scholars API - We'll implement this later
    DUKE_SCHOLARS_BASE_URL: str = os.getenv(
        "DUKE_SCHOLARS_BASE_URL",
        "https://scholars.duke.edu/widgets/api/v0.9"
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
