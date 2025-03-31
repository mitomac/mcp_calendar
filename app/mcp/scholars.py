"""
Scholars MCP implementation
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import httpx
from app.config import settings
from app.models.scholars import ScholarDetails, ScholarPublication, ScholarGrant, ScholarEducation
from app.mcp.directory import directory_mcp

logger = logging.getLogger("duke_scholars_mcp")

class ScholarsMCP:
    def __init__(self):
        self.base_url = settings.DUKE_SCHOLARS_BASE_URL
        self.cache_duration = timedelta(hours=settings.REFERENCE_CACHE_TTL / 3600)  # Convert seconds to hours
        
        # Cache for scholars data
        self.publications_cache: Dict[str, Dict[str, Any]] = {}  # duid -> Results
        self.publications_cache_timestamp: Dict[str, datetime] = {}  # duid -> Timestamp
        
        self.grants_cache: Dict[str, Dict[str, Any]] = {}  # duid -> Results
        self.grants_cache_timestamp: Dict[str, datetime] = {}  # duid -> Timestamp
        
        self.details_cache: Dict[str, Dict[str, Any]] = {}  # duid -> Results
        self.details_cache_timestamp: Dict[str, datetime] = {}  # duid -> Timestamp
        
        self.debug_mode = settings.DEBUG

    async def _is_cache_fresh(self, cache_timestamp: Optional[datetime]) -> bool:
        """Check if a cache timestamp is fresh"""
        if cache_timestamp is None:
            return False
        return datetime.now() - cache_timestamp <= self.cache_duration

    async def _find_duid_from_directory(self, query: str) -> Optional[str]:
        """
        Find a person's DUID by searching the directory
        
        :param query: Name, NetID, or other identifier
        :return: DUID if found, None otherwise
        """
        directory_results = await directory_mcp.search_directory(query)
        
        # Check if we got valid results
        if "error" in directory_results or not directory_results.get("results"):
            logger.warning(f"No directory results found for query: {query}")
            return None
            
        # Use the first result (most relevant match)
        # In a more sophisticated implementation, we might want to handle multiple matches
        if directory_results["results"]:
            return directory_results["results"][0].get("duid")
            
        return None

    async def get_scholar_publications(self, duid_or_query: str, count: int = 10) -> Dict[str, Any]:
        """
        Get publications for a Duke scholar
        
        :param duid_or_query: DUID or search query to find a person
        :param count: Number of publications to return (default: 10)
        :return: Dictionary with publications data
        """
        # Check if input is a DUID or a search query
        duid = duid_or_query
        if not duid_or_query.isdigit():
            # If not a numeric DUID, try to find it from the directory
            found_duid = await self._find_duid_from_directory(duid_or_query)
            if not found_duid:
                return {"error": f"Could not find a person matching: {duid_or_query}", 
                        "publications": [], "count": 0, "duid": duid_or_query}
            duid = found_duid
        
        # Check cache first
        cache_key = f"{duid}_{count}"
        if cache_key in self.publications_cache and await self._is_cache_fresh(self.publications_cache_timestamp.get(cache_key)):
            logger.info(f"Using cached publications for DUID: {duid}")
            return self.publications_cache[cache_key]

        try:
            # Construct API URL
            url = f"{self.base_url}/people/publications/{count}.json"
            
            # Set up required parameters
            params = {"uri": duid}
            
            # Make the API call
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                   
                    #fix from chatgpt if data comes back as a raaw list without an item key
                    print(f"Scholars API response type: {type(data)}")
                    items = data if isinstance(data, list) else data.get("items", [])



                    # Process data into our model format
                    publications = []
                    # for pub in data.get("items", []):
                    for pub in items:
                        publication = ScholarPublication(
                            title=pub.get("label", ""),
                            authors=self._extract_authors(pub),
                            journal=self._extract_journal(pub),
                            year=self._extract_year(pub),
                            citation=self._extract_citation(pub),
                            url=pub.get("uri", ""),
                            publication_type=self._extract_publication_type(pub)
                        )
                        publications.append(publication.dict())
                    
                    # Cache the results
                    response_data = {"publications": publications, "count": len(publications), "duid": duid}
                    self.publications_cache[cache_key] = response_data
                    self.publications_cache_timestamp[cache_key] = datetime.now()
                    
                    return response_data
                else:
                    error_data = {"error": f"Error querying publications: Status {response.status_code}", 
                                 "publications": [], "count": 0, "duid": duid}
                    return error_data
                
        except Exception as e:
            logger.error(f"Error in publications query: {str(e)}")
            return {"error": f"Exception in publications query: {str(e)}", 
                   "publications": [], "count": 0, "duid": duid}

    async def get_scholar_grants(self, duid_or_query: str, count: int = 10) -> Dict[str, Any]:
        """
        Get grants for a Duke scholar
        
        :param duid_or_query: DUID or search query to find a person
        :param count: Number of grants to return (default: 10)
        :return: Dictionary with grants data
        """
        # Check if input is a DUID or a search query
        duid = duid_or_query
        if not duid_or_query.isdigit():
            # If not a numeric DUID, try to find it from the directory
            found_duid = await self._find_duid_from_directory(duid_or_query)
            if not found_duid:
                return {"error": f"Could not find a person matching: {duid_or_query}", 
                        "grants": [], "count": 0, "duid": duid_or_query}
            duid = found_duid
        
        # Check cache first
        cache_key = f"{duid}_{count}"
        if cache_key in self.grants_cache and await self._is_cache_fresh(self.grants_cache_timestamp.get(cache_key)):
            logger.info(f"Using cached grants for DUID: {duid}")
            return self.grants_cache[cache_key]

        try:
            # Construct API URL
            url = f"{self.base_url}/people/grants/{count}.json"
            
            # Set up required parameters
            params = {"uri": duid}
            
            # Make the API call
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    #same issue with pubs not items in json
                    items = data if isinstance(data, list) else data.get("items", [])
                    
                    # Process data into our model format
                    grants = []
                    for grant in items:
                        attributes = grant.get("attributes", {})
                        grant_obj = ScholarGrant(
                            title=grant.get("label", ""),
                            awarded_by=attributes.get("awardedBy", ""),
                            role=attributes.get("roleName", ""),
                            start_date=self._format_date(attributes.get("startDate")),
                            end_date=self._format_date(attributes.get("endDate")),
                            administered_by=attributes.get("administeredBy", "")
                        )
                        grants.append(grant_obj.dict())
                    
                    # Cache the results
                    response_data = {"grants": grants, "count": len(grants), "duid": duid}
                    self.grants_cache[cache_key] = response_data
                    self.grants_cache_timestamp[cache_key] = datetime.now()
                    
                    return response_data
                else:
                    error_data = {"error": f"Error querying grants: Status {response.status_code}", 
                                 "grants": [], "count": 0, "duid": duid}
                    return error_data
                
        except Exception as e:
            logger.error(f"Error in grants query: {str(e)}")
            return {"error": f"Exception in grants query: {str(e)}", 
                   "grants": [], "count": 0, "duid": duid}

    async def get_scholar_details(self, duid_or_query: str) -> Dict[str, Any]:
        """
        Get detailed information about a Duke scholar
        
        :param duid_or_query: DUID or search query to find a person
        :return: Dictionary with scholar details
        """
        # Check if input is a DUID or a search query
        duid = duid_or_query
        if not duid_or_query.isdigit():
            # If not a numeric DUID, try to find it from the directory
            found_duid = await self._find_duid_from_directory(duid_or_query)
            if not found_duid:
                return {"error": f"Could not find a person matching: {duid_or_query}", 
                        "scholar": None, "duid": duid_or_query}
            duid = found_duid
        
        # Check cache first
        if duid in self.details_cache and await self._is_cache_fresh(self.details_cache_timestamp.get(duid)):
            logger.info(f"Using cached details for DUID: {duid}")
            return self.details_cache[duid]

        try:
            # Construct API URL
            url = f"{self.base_url}/people/complete/1.json"
            
            # Set up required parameters
            params = {"uri": duid}
            
            # Make the API call
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if we have items
                    if not data.get("items") or len(data["items"]) == 0:
                        return {"error": "No details found for this person", "scholar": None, "duid": duid}
                    
                    # Get the first (and should be only) item
                    person_data = data["items"][0]
                    attributes = person_data.get("attributes", {})
                    
                    # Extract research interests
                    research_interests = []
                    for interest in person_data.get("researchAreas", []):
                        if interest.get("label"):
                            research_interests.append(interest["label"])
                    
                    # Extract education
                    education = []
                    for edu in person_data.get("educations", []):
                        edu_attributes = edu.get("attributes", {})
                        degree = edu_attributes.get("degree", "")
                        institution = self._get_nested_value(edu_attributes, ["institution", "label"])
                        year = self._get_year_from_date(edu_attributes.get("endDate"))
                        
                        education_obj = ScholarEducation(
                            degree=degree,
                            institution=institution,
                            year=year,
                            description=f"{degree} {institution}" + (f" ({year})" if year else "")
                        )
                        education.append(education_obj.dict())
                    
                    # Create scholar details
                    scholar = ScholarDetails(
                        duid=duid,
                        name=attributes.get("name", ""),
                        title=attributes.get("preferredTitle", ""),
                        overview=attributes.get("overview", ""),
                        department=self._get_department(person_data),
                        email=attributes.get("primaryEmail", ""),
                        phone=self._get_phone(person_data),
                        office=self._get_office_location(person_data),
                        research_interests=research_interests,
                        education=education,
                        profile_url=person_data.get("uri", ""),
                        image_url=attributes.get("imageUri", "")
                    )
                    
                    # Cache the results
                    response_data = {"scholar": scholar.dict(), "duid": duid}
                    self.details_cache[duid] = response_data
                    self.details_cache_timestamp[duid] = datetime.now()
                    
                    return response_data
                else:
                    error_data = {"error": f"Error querying scholar details: Status {response.status_code}", 
                                 "scholar": None, "duid": duid}
                    return error_data
                
        except Exception as e:
            logger.error(f"Error in scholar details query: {str(e)}")
            return {"error": f"Exception in scholar details query: {str(e)}", 
                   "scholar": None, "duid": duid}

    # Helper methods for extracting data from complex API responses
    
    def _extract_authors(self, publication: Dict) -> List[str]:
        """Extract authors from publication data"""
        attrs = publication.get("attributes", {})
        author_list = attrs.get("authorList", "")
        if author_list:
            return [a.strip() for a in author_list.split(";")]
        return []

    def _extract_journal(self, publication: Dict) -> str:
        """Extract journal from publication data"""
        attrs = publication.get("attributes", {})
        return attrs.get("publishedIn", "")

    def _extract_year(self, publication: Dict) -> str:
        """Extract year from publication data"""
        attrs = publication.get("attributes", {})
        year = attrs.get("year", "")
        # Year may be ISO format date, extract just the year
        if year and "-" in year:
            year = year.split("-")[0]
        return year

    def _extract_citation(self, publication: Dict) -> str:
        """Extract citation from publication data"""
        attrs = publication.get("attributes", {})
        # Try different citation formats
        citation = attrs.get("apaCitation", "")
        if not citation:
            citation = attrs.get("chicagoCitation", "")
        if not citation:
            citation = attrs.get("mlaCitation", "")
        # Clean up HTML from citation
        citation = citation.replace("<div>", "").replace("</div>", "")
        citation = citation.replace("<a href=\"", "").replace("</a>", "")
        citation = citation.replace("<i>", "").replace("</i>", "")
        # Remove any remaining HTML tags
        import re
        citation = re.sub(r'<.*?>', '', citation)
        return citation

    def _extract_publication_type(self, publication: Dict) -> str:
        """Extract publication type from publication data"""
        vivo_type = publication.get("vivoType", "")
        if vivo_type:
            # Extract the last part of the URI
            parts = vivo_type.split("/")
            if parts:
                return parts[-1]
        return ""

    def _format_date(self, date_str: Optional[str]) -> str:
        """Format date string to readable format"""
        if not date_str:
            return ""
        # Handle ISO format dates
        if "T" in date_str:
            date_str = date_str.split("T")[0]
        # Format YYYY-MM-DD to readable format
        try:
            year, month, day = date_str.split("-")
            months = ["January", "February", "March", "April", "May", "June",
                     "July", "August", "September", "October", "November", "December"]
            if 1 <= int(month) <= 12:
                return f"{months[int(month)-1]} {int(day)}, {year}"
        except:
            pass
        return date_str

    def _get_nested_value(self, data: Dict, keys: List[str]) -> str:
        """Get a nested value from a dictionary using a list of keys"""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return ""
        return current if isinstance(current, str) else ""

    def _get_year_from_date(self, date_str: Optional[str]) -> str:
        """Extract year from date string"""
        if not date_str:
            return ""
        if "T" in date_str:
            date_str = date_str.split("T")[0]
        if "-" in date_str:
            return date_str.split("-")[0]
        return date_str

    def _get_department(self, person_data: Dict) -> str:
        """Extract department from person data"""
        departments = person_data.get("departments", [])
        if departments and len(departments) > 0:
            return departments[0].get("label", "")
        return ""

    def _get_phone(self, person_data: Dict) -> str:
        """Extract phone from person data"""
        # Check for phone in attributes
        attributes = person_data.get("attributes", {})
        if "phone" in attributes:
            return attributes["phone"]
        return ""

    def _get_office_location(self, person_data: Dict) -> str:
        """Extract office location from person data"""
        # Check for office location in attributes
        attributes = person_data.get("attributes", {})
        if "officeLocation" in attributes:
            return attributes["officeLocation"]
        
        # Try to find in addresses
        addresses = person_data.get("addresses", [])
        for address in addresses:
            if "work_location" in address.get("uri", ""):
                return address.get("label", "")
        return ""

# Initialize the ScholarsMCP instance
scholars_mcp = ScholarsMCP()
