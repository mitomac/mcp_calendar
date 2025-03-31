"""
title: Duke Scholars Tool
author: Claude
author_url: https://www.anthropic.com
description: A tool for accessing Duke University scholars' academic information.
version: 1.0.0
license: MIT
required_open_webui_version: 0.4.0
requirements: requests

USAGE INSTRUCTIONS FOR LLM:
This tool helps you find academic and research information about faculty and scholars at Duke University.

FOLLOW THESE EXACT STEPS WHEN ANSWERING SCHOLAR QUERIES:
1. IDENTIFY THE SCHOLAR: Use a name or NetID to find information about a Duke scholar.
   You can search by name or NetID - the tool will automatically handle finding the correct person.

2. GET SCHOLARLY INFORMATION: Choose which information to retrieve based on the query:
   a. get_scholar_details(name_or_duid) - Get general information about a scholar
   b. get_scholar_publications(name_or_duid) - Get the scholar's publications
   c. get_scholar_grants(name_or_duid) - Get the scholar's grants

3. PRESENT RESULTS APPROPRIATELY:
   - For general queries: Present an overview of the scholar's research interests, education, and position
   - For publication queries: Highlight recent and significant publications with proper citations
   - For grant queries: Present current grants with roles and sponsors
   - Format information clearly and concisely

HANDLING COMMON QUERIES:
- "Tell me about Professor Smith's research" → get_scholar_details() to find research interests
- "What has Jane Doe published recently?" → get_scholar_publications() to get recent publications
- "What grants does Dr. Johnson have?" → get_scholar_grants() to list active grants
- "What is Professor Lee's background?" → get_scholar_details() to find education and position history

EFFICIENT WORKFLOW:
- You can search directly by name - no need to first get a DUID
- If multiple people have similar names, you may need to clarify with the user
- Focus on presenting the most relevant information first
- For publications, prioritize recent and significant works

SPECIAL CONSIDERATIONS:
- Research overviews can be lengthy - summarize them when appropriate
- When listing publications, include proper citations
- For grants, emphasize the scholar's role (PI, Co-I, etc.)
- Include both current and pending grants when relevant
"""

import requests
import json
from typing import Dict, List, Optional, Any


class Tools:
    def __init__(self):
        self.citation = True
        self.mcp_url = "http://macalpine.colab.duke.edu:8000/api/v1/scholars"  # URL to the MCP server

    def get_scholar_details(self, duid_or_query: str) -> str:
        """
        Get detailed information about a Duke scholar
        
        :param duid_or_query: DUID or name/NetID to find a person
        :return: JSON string with detailed scholar information
        """
        try:
            response = requests.get(
                f"{self.mcp_url}/details",
                params={"duid_or_query": duid_or_query}
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            return json.dumps({"error": str(e), "scholar": None, "duid": duid_or_query})

    def get_scholar_publications(self, duid_or_query: str, count: int = 10) -> str:
        """
        Get publications for a Duke scholar
        
        :param duid_or_query: DUID or name/NetID to find a person
        :param count: Number of publications to return (default: 10)
        :return: JSON string with publications data
        """
        try:
            response = requests.get(
                f"{self.mcp_url}/publications",
                params={"duid_or_query": duid_or_query, "count": count}
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            return json.dumps({"error": str(e), "publications": [], "count": 0, "duid": duid_or_query})

    def get_scholar_grants(self, duid_or_query: str, count: int = 10) -> str:
        """
        Get grants for a Duke scholar
        
        :param duid_or_query: DUID or name/NetID to find a person
        :param count: Number of grants to return (default: 10)
        :return: JSON string with grants data
        """
        try:
            response = requests.get(
                f"{self.mcp_url}/grants",
                params={"duid_or_query": duid_or_query, "count": count}
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            return json.dumps({"error": str(e), "grants": [], "count": 0, "duid": duid_or_query})


if __name__ == "__main__":
    print("Scholars tool initialized")
