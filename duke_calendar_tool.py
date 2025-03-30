"""
title: Duke Calendar Tool
author: Claude
author_url: https://www.anthropic.com
description: A tool for querying Duke University calendar events via MCP server
version: 1.0.0
license: MIT
required_open_webui_version: 0.4.0
requirements: requests
"""

import requests
import json
from typing import Dict, List, Optional, Any, Union

class Tools:
    def __init__(self):
        self.citation = True
        self.mcp_url = "http://localhost:8000/api/v1/calendar"  # URL to the MCP server
        self.reference_data = self._load_reference_data()
    
    def _load_reference_data(self) -> Dict[str, List[str]]:
        """Load reference data for groups and categories"""
        try:
            # Get group reference data
            group_response = requests.get(f"{self.mcp_url}/reference/groups")
            groups = group_response.json().get("data", [])
            
            # Get category reference data
            category_response = requests.get(f"{self.mcp_url}/reference/categories")
            categories = category_response.json().get("data", [])
            
            return {
                "groups": groups,
                "categories": categories
            }
        except Exception as e:
            print(f"Error loading reference data: {str(e)}")
            # Fallback to minimal reference data
            return {
                "groups": ["Duke Law School", "School of Medicine (SOM)"],
                "categories": ["Lecture/Talk", "Conference/Symposium"]
            }
    
    def query_calendar(self, 
                      query: str,
                      time_range: str = "today", 
                      groups: str = "", 
                      categories: str = "") -> str:
        """
        Query the Duke Calendar using the LLM's interpretation of parameters
        
        IMPORTANT: The LLM should identify relevant groups and categories from the reference data
        
        :param query: Original user query for context
        :param time_range: Time range (today, tomorrow, this week, next week, etc.)
        :param groups: Comma-separated official group names (matched from reference list)
        :param categories: Comma-separated official category names (matched from reference list)
        :return: JSON string with event information
        """
        try:
            # Convert comma-separated strings to lists
            group_list = [g.strip() for g in groups.split(",")] if groups else []
            category_list = [c.strip() for c in categories.split(",")] if categories else []
            
            # Filter out empty strings
            group_list = [g for g in group_list if g]
            category_list = [c for c in category_list if c]
            
            # Prepare the request to the MCP
            mcp_request = {
                "query": query,
                "time_range": time_range,
                "groups": group_list,
                "categories": category_list
            }
            
            # Call the MCP
            response = requests.post(
                f"{self.mcp_url}/query", 
                json=mcp_request
            )
            
            # Return the response
            return response.text
            
        except Exception as e:
            return json.dumps({
                "error": f"Error querying calendar: {str(e)}",
                "events": []
            })
    
    def get_available_groups(self) -> str:
        """
        Get the full list of available groups/departments at Duke
        
        :return: JSON string with all valid group names
        """
        return json.dumps({"groups": self.reference_data.get("groups", [])})
    
    def get_available_categories(self) -> str:
        """
        Get the full list of available event categories at Duke
        
        :return: JSON string with all valid category names
        """
        return json.dumps({"categories": self.reference_data.get("categories", [])})


if __name__ == "__main__":
    from inspect import signature

    tool = Tools()
    sig = signature(tool.query_calendar)
    print("Function signature for query_calendar():")
    print(sig)

