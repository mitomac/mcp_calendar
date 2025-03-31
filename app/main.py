"""
Duke MCP Server - Main Application Entry Point
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import calendar, directory, scholars
from app.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("duke_mcp")

# Initialize FastAPI app
app = FastAPI(
    title="Duke MCP Server",
    description="MCP Server for Duke Services OpenWebUI Integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(calendar.router, prefix=f"{settings.API_V1_STR}/calendar")
app.include_router(directory.router, prefix=f"{settings.API_V1_STR}/directory")
app.include_router(scholars.router, prefix=f"{settings.API_V1_STR}/scholars")

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "duke-mcp"}

@app.get("/")
def root():
    """Root endpoint with links to docs"""
    return {
        "message": "Duke MCP Server is running",
        "documentation": "/docs",
        "health": "/health",
        "services": ["calendar", "directory"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="67.159.65.145", port=8000, reload=True)
