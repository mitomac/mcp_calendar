"""
API routes for Duke Directory
"""
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.mcp.directory import directory_mcp
from app.models.directory import DirectorySearchResponse, DetailedPersonResponse

logger = logging.getLogger("duke_directory_mcp")
router = APIRouter(tags=["directory"])

@router.get("/search", response_model=DirectorySearchResponse)
async def search_directory(query: str):
    """
    Search the Duke directory
    
    :param query: Name, NetID, or other identifier
    :return: Directory search results
    """
    try:
        results = await directory_mcp.search_directory(query)
        
        if "error" in results and not results.get("results"):
            # Serious error with no results
            raise HTTPException(status_code=500, detail=results["error"])
            
        return results
    except Exception as e:
        logger.error(f"Error in directory search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/person/{ldapkey}", response_model=DetailedPersonResponse)
async def get_person_details(ldapkey: str):
    """
    Get detailed information about a person
    
    :param ldapkey: The ldapkey for the person
    :return: Detailed person information
    """
    try:
        results = await directory_mcp.get_person_details(ldapkey)
        
        if "error" in results and not results.get("person"):
            # Serious error with no person data
            raise HTTPException(status_code=404, detail=results["error"])
            
        return results
    except Exception as e:
        logger.error(f"Error in person details endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/netid/{netid}", response_model=DirectorySearchResponse)
async def search_by_netid(netid: str):
    """
    Search for a person by their NetID
    
    :param netid: The NetID to search for
    :return: Directory search results
    """
    try:
        results = await directory_mcp.search_by_netid(netid)
        
        if "error" in results and not results.get("results"):
            # Serious error with no results
            raise HTTPException(status_code=500, detail=results["error"])
            
        return results
    except Exception as e:
        logger.error(f"Error in netid search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/name/{name}", response_model=DirectorySearchResponse)
async def search_by_name(name: str):
    """
    Search for a person by their name
    
    :param name: The name to search for
    :return: Directory search results
    """
    try:
        results = await directory_mcp.search_by_name(name)
        
        if "error" in results and not results.get("results"):
            # Serious error with no results
            raise HTTPException(status_code=500, detail=results["error"])
            
        return results
    except Exception as e:
        logger.error(f"Error in name search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
