"""
Data models for the Duke Scholars MCP
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ScholarPublication(BaseModel):
    """Model for a scholar's publication"""
    title: str
    authors: Optional[List[str]] = None
    journal: Optional[str] = None
    year: Optional[str] = None
    citation: Optional[str] = None
    url: Optional[str] = None
    publication_type: Optional[str] = None


class ScholarGrant(BaseModel):
    """Model for a scholar's grant"""
    title: str
    awarded_by: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    administered_by: Optional[str] = None


class ScholarEducation(BaseModel):
    """Model for a scholar's education"""
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None
    description: Optional[str] = None


class ScholarDetails(BaseModel):
    """Model for detailed scholar information"""
    duid: str
    name: str
    title: Optional[str] = None
    overview: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    office: Optional[str] = None
    research_interests: Optional[List[str]] = None
    education: Optional[List[ScholarEducation]] = None
    profile_url: Optional[str] = None
    image_url: Optional[str] = None


class PublicationsResponse(BaseModel):
    """Response model for publications"""
    publications: List[ScholarPublication]
    count: int
    duid: str


class GrantsResponse(BaseModel):
    """Response model for grants"""
    grants: List[ScholarGrant]
    count: int
    duid: str


class ScholarDetailsResponse(BaseModel):
    """Response model for scholar details"""
    scholar: ScholarDetails
    duid: str
