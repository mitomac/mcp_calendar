"""
title: Duke Directory Tool
author: Claude
author_url: https://www.anthropic.com
description: A tool for accessing Duke University directory information.
version: 1.0.0
license: MIT
required_open_webui_version: 0.4.0
requirements: requests

USAGE INSTRUCTIONS FOR LLM:
This tool helps you find people and their contact information in the Duke University directory.

FOLLOW THESE EXACT STEPS WHEN ANSWERING DIRECTORY QUERIES:
1. SEARCH FOR PEOPLE: Use search_directory() with a name or netID to find people in the directory.
   Example: search_directory("Smith") → Returns people with "Smith" in their name
   Example: search_directory("abc123") → Returns the person with NetID "abc123"

2. PROCESS SEARCH RESULTS:
   - If exactly ONE person is found, ALWAYS get their detailed information using get_person_details().
   - If MULTIPLE people are found, ask the user which person they're interested in. Include their departments to help distinguish between people.
   - If NO people are found, suggest alternative search terms or spellings.

3. GET DETAILED INFORMATION: Only after identifying the specific person, use get_person_details() with the ldapkey.
   Example: get_person_details("39eb57d4-1dd2-11b2-be77-9442cd793b76") → Returns full contact information

4. PRESENT RESULTS APPROPRIATELY:
   - Format contact information clearly and include name, title, department, email, phone, and office location
   - For faculty, prominently display their titles and departmental affiliations
   - Organize information in a logical order (e.g., name, title, contact details, location)

HANDLING COMMON QUERIES:
- "How do I contact Professor Smith?" → First search for "Smith" - if one result, get details automatically; if multiple results, ask which Smith
- "What's Jane Doe's email?" → Search for "Jane Doe", then automatically get details if only one match
- "Where is Dr. Johnson's office?" → Search for "Johnson", ask which Johnson if multiple results found

EFFICIENT WORKFLOW:
- Always check the number of results before proceeding
- If exactly one result, automatically get detailed information
- If multiple results, ask for clarification
- If no results, suggest alternative search terms
"""

import requests
import json
from typing import Dict, List, Optional, Any


class Tools:
    def __init__(self):
        self.citation = True
        self.mcp_url = "http://macalpine.colab.duke.edu:8000/api/v1/directory"  # URL to the MCP server

    def search_directory(self, query: str) -> str:
        """
        Search the Duke directory for people matching the query
        
        :param query: Name, NetID, or other identifier
        :return: JSON string with search results
        """
        try:
            response = requests.get(
                f"{self.mcp_url}/search",
                params={"query": query}
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            return json.dumps({"error": str(e), "results": [], "count": 0, "query": query})

    def get_person_details(self, ldapkey: str) -> str:
        """
        Get detailed information about a person using their ldapkey
        
        :param ldapkey: The ldapkey for the person
        :return: JSON string with detailed person information
        """
        try:
            response = requests.get(
                f"{self.mcp_url}/person/{ldapkey}"
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            return json.dumps({"error": str(e), "person": None, "ldapkey": ldapkey})

    def search_by_netid(self, netid: str) -> str:
        """
        Search for a person by their NetID
        
        :param netid: The NetID to search for
        :return: JSON string with search results
        """
        try:
            response = requests.get(
                f"{self.mcp_url}/netid/{netid}"
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            return json.dumps({"error": str(e), "results": [], "count": 0, "query": netid})

    def search_by_name(self, name: str) -> str:
        """
        Search for a person by their name
        
        :param name: The name to search for
        :return: JSON string with search results
        """
        try:
            response = requests.get(
                f"{self.mcp_url}/name/{name}"
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            return json.dumps({"error": str(e), "results": [], "count": 0, "query": name})


if __name__ == "__main__":
    print("Directory tool initialized")
