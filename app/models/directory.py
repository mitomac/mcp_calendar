"""
Data models for the Duke Directory MCP
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class DirectoryPerson(BaseModel):
    """Basic person information from directory search"""
    ldapkey: str
    sn: str  # surname
    givenName: str
    duid: str
    netid: str
    display_name: str
#    url: str  #commented out because url is uselesswithout token and llm was prioritzing the link


class DirectorySearchResponse(BaseModel):
    """Response model for directory search results"""
    results: List[DirectoryPerson]
    count: int
    query: str


class DetailedPerson(BaseModel):
    """Detailed person information from LDAP lookup"""
    ldapkey: str
    sn: str  # surname
    givenName: str
    duid: str
    netid: str
    display_name: str
    nickname: Optional[str] = None
    titles: Optional[List[str]] = None
    primary_affiliation: Optional[str] = None
    emails: Optional[List[str]] = None
    post_office_box: Optional[List[str]] = None
    address: Optional[List[str]] = None
    phones: Optional[List[str]] = None
    department: Optional[str] = None
#    url: str


class DetailedPersonResponse(BaseModel):
    """Response model for detailed person information"""
    person: DetailedPerson
    ldapkey: str
