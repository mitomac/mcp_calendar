"""
Directory MCP implementation
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import httpx
from app.config import settings
from app.models.directory import DirectoryPerson, DetailedPerson

logger = logging.getLogger("duke_directory_mcp")

class DirectoryMCP:
    def __init__(self):
        self.api_key = settings.DUKE_DIRECTORY_API_KEY
        self.base_url = settings.DUKE_DIRECTORY_BASE_URL
        self.cache_duration = timedelta(hours=settings.REFERENCE_CACHE_TTL / 3600)  # Convert seconds to hours
        
        # Cache for directory search results
        self.directory_cache: Dict[str, Dict[str, Any]] = {}  # Query -> Results
        self.directory_cache_timestamp: Dict[str, datetime] = {}  # Query -> Timestamp
        
        # Cache for detailed person results
        self.person_cache: Dict[str, Dict[str, Any]] = {}  # ldapkey -> Results
        self.person_cache_timestamp: Dict[str, datetime] = {}  # ldapkey -> Timestamp
        
        self.debug_mode = settings.DEBUG

    async def _is_cache_fresh(self, cache_timestamp: Optional[datetime]) -> bool:
        """Check if a cache timestamp is fresh"""
        if cache_timestamp is None:
            return False
        return datetime.now() - cache_timestamp <= self.cache_duration

    async def search_directory(self, query: str) -> Dict[str, Any]:
        """
        Search the Duke directory for people matching the query
        
        :param query: Name, NetID, or other identifier
        :return: Dictionary with search results
        """
        # Check cache first
        cache_key = f"dir_search_{query}"
        if cache_key in self.directory_cache and await self._is_cache_fresh(self.directory_cache_timestamp.get(cache_key)):
            logger.info(f"Using cached directory results for query: {query}")
            return self.directory_cache[cache_key]

        try:
            # Call to search directory
            params = {"q": query, "access_token": self.api_key}
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code != 200:
                    return {"error": f"Error in directory search: {response.status_code}", "results": [], "count": 0, "query": query}

                results = response.json()
                
                # Convert results to DirectoryPerson objects for validation
                validated_results = []
                for result in results:
                    try:
                        person = DirectoryPerson(**result)
                        validated_results.append(person.dict())
                    except Exception as e:
                        logger.warning(f"Validation error for result: {result}. Error: {e}")
                
                # Cache the results
                response_data = {"results": validated_results, "count": len(validated_results), "query": query}
                self.directory_cache[cache_key] = response_data
                self.directory_cache_timestamp[cache_key] = datetime.now()
                
                return response_data
                
        except Exception as e:
            logger.error(f"Error in directory search: {str(e)}")
            return {"error": str(e), "results": [], "count": 0, "query": query}

    async def get_person_details(self, ldapkey: str) -> Dict[str, Any]:
        """
        Get detailed information about a person using their ldapkey
        
        :param ldapkey: The ldapkey for the person
        :return: Dictionary with detailed person information
        """
        # Check cache first
        if ldapkey in self.person_cache and await self._is_cache_fresh(self.person_cache_timestamp.get(ldapkey)):
            logger.info(f"Using cached person details for ldapkey: {ldapkey}")
            return self.person_cache[ldapkey]

        try:
            # Call to get detailed person information
            detail_url = f"{self.base_url}/{ldapkey}"
            params = {"access_token": self.api_key}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(detail_url, params=params)
                
                if response.status_code != 200:
                    return {"error": f"Error getting person details: {response.status_code}", "person": None, "ldapkey": ldapkey}

                person_data = response.json()
                
                # Validate person data
                try:
                    person = DetailedPerson(**person_data)
                    
                    # Cache the results
                    response_data = {"person": person.dict(), "ldapkey": ldapkey}
                    self.person_cache[ldapkey] = response_data
                    self.person_cache_timestamp[ldapkey] = datetime.now()
                    
                    return response_data
                except Exception as e:
                    logger.warning(f"Validation error for person data: {person_data}. Error: {e}")
                    return {"error": f"Validation error: {str(e)}", "person": None, "ldapkey": ldapkey}
                
        except Exception as e:
            logger.error(f"Error getting person details: {str(e)}")
            return {"error": str(e), "person": None, "ldapkey": ldapkey}

    async def search_by_netid(self, netid: str) -> Dict[str, Any]:
        """
        Search for a person by their NetID
        
        :param netid: The NetID to search for
        :return: Dictionary with search results
        """
        return await self.search_directory(netid)

    async def search_by_name(self, name: str) -> Dict[str, Any]:
        """
        Search for a person by their name
        
        :param name: The name to search for
        :return: Dictionary with search results
        """
        return await self.search_directory(name)

# Initialize the DirectoryMCP instance
directory_mcp = DirectoryMCP()
