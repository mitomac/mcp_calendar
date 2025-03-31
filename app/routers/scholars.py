"""
API routes for Duke Scholars
"""
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.mcp.scholars import scholars_mcp
from app.models.scholars import PublicationsResponse, GrantsResponse, ScholarDetailsResponse

logger = logging.getLogger("duke_scholars_mcp")
router = APIRouter(tags=["scholars"])

@router.get("/publications", response_model=PublicationsResponse)
async def get_publications(duid_or_query: str, count: Optional[int] = Query(10, ge=1, le=100)):
    """
    Get publications for a Duke scholar
    
    :param duid_or_query: DUID or search query to find a person
    :param count: Maximum number of publications to return
    :return: Scholar publications
    """
    try:
        results = await scholars_mcp.get_scholar_publications(duid_or_query, count)
        
        if "error" in results and not results.get("publications"):
            # Serious error with no results
            raise HTTPException(status_code=404, detail=results["error"])
            
        return results
    except Exception as e:
        logger.error(f"Error in publications endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/grants", response_model=GrantsResponse)
async def get_grants(duid_or_query: str, count: Optional[int] = Query(10, ge=1, le=100)):
    """
    Get grants for a Duke scholar
    
    :param duid_or_query: DUID or search query to find a person
    :param count: Maximum number of grants to return
    :return: Scholar grants
    """
    try:
        results = await scholars_mcp.get_scholar_grants(duid_or_query, count)
        
        if "error" in results and not results.get("grants"):
            # Serious error with no results
            raise HTTPException(status_code=404, detail=results["error"])
            
        return results
    except Exception as e:
        logger.error(f"Error in grants endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/details", response_model=ScholarDetailsResponse)
async def get_scholar_details(duid_or_query: str):
    """
    Get detailed information about a Duke scholar
    
    :param duid_or_query: DUID or search query to find a person
    :return: Detailed scholar information
    """
    try:
        results = await scholars_mcp.get_scholar_details(duid_or_query)
        
        if "error" in results and not results.get("scholar"):
            # Serious error with no scholar data
            raise HTTPException(status_code=404, detail=results["error"])
            
        return results
    except Exception as e:
        logger.error(f"Error in scholar details endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
