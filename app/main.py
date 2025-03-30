"""
Duke Calendar MCP Server - Main Application Entry Point
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import calendar
from app.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("duke_calendar_mcp")

# Initialize FastAPI app
app = FastAPI(
    title="Duke Calendar MCP Server",
    description="MCP Server for Duke Calendar OpenWebUI Integration",
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

# Include router
app.include_router(calendar.router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "duke-calendar-mcp"}

@app.get("/")
def root():
    """Root endpoint with links to docs"""
    return {
        "message": "Duke Calendar MCP Server is running",
        "documentation": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
