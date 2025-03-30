"""
title: Duke Calendar Tool
author: Claude
author_url: https://www.anthropic.com
description: A tool for querying Duke University calendar events via MCP server. It allows language models to retrieve time-bound group and category filters and request event details based on LLM-interpreted user queries.
version: 1.0.0
license: MIT
required_open_webui_version: 0.4.0
requirements: requests
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import date

class Tools:
    def __init__(self):
        self.citation = True
        self.mcp_url = "http://localhost:8000/api/v1/calendar"  # URL to the MCP server

    def get_filters_by_date(self, start_date: str, end_date: str) -> str:
        """
        Retrieve active groups and categories within a specific date range.

        The language model should:
        - Convert natural timeframes (e.g., "this week") into two ISO8601 dates
        - Call this method with those dates
        - Present the results or use them to select filters in later queries

        :param start_date: Start date in ISO format (YYYY-MM-DD)
        :param end_date: End date in ISO format (YYYY-MM-DD)
        :return: JSON string with 'groups' and 'categories', each mapping to a list of event IDs
        """
        try:
            response = requests.get(
                f"{self.mcp_url}/filters-with-ids",
                params={"start_date": start_date, "end_date": end_date}
            )
            return response.text
        except Exception as e:
            return json.dumps({"error": f"Error fetching filters: {str(e)}"})

    def query_calendar(self,
                       query: str,
                       start_date: str,
                       end_date: str,
                       groups: str = "",
                       categories: str = "") -> str:
        """
        Query the Duke Calendar using the LLM's interpretation of user intent.

        The model should:
        1. Convert time ranges like "this week" into specific dates.
        2. Optionally call `get_filters_by_date` to get valid filters.
        3. Pass user-selected or model-selected filters into this method.

        :param query: Original user query (natural language)
        :param start_date: ISO start date for filtering events
        :param end_date: ISO end date for filtering events
        :param groups: Comma-separated list of official sponsor names
        :param categories: Comma-separated list of official category names
        :return: JSON string of event results
        """
        try:
            group_list = [g.strip() for g in groups.split(",") if g.strip()]
            category_list = [c.strip() for c in categories.split(",") if c.strip()]

            mcp_request = {
                "query": query,
                "start_date": start_date,
                "end_date": end_date,
                "groups": group_list,
                "categories": category_list
            }

            response = requests.post(
                f"{self.mcp_url}/query",
                json=mcp_request
            )
            return response.text

        except Exception as e:
            return json.dumps({
                "error": f"Error querying calendar: {str(e)}",
                "events": []
            })

    def get_available_groups(self) -> str:
        """
        Return static list of groups (sponsors). Only used if no date filtering is desired.
        :return: JSON string with group names
        """
        try:
            response = requests.get(f"{self.mcp_url}/reference/groups")
            return json.dumps({"groups": response.json().get("data", [])})
        except Exception as e:
            return json.dumps({"groups": [], "error": str(e)})

    def get_available_categories(self) -> str:
        """
        Return static list of event categories. Only used if no date filtering is desired.
        :return: JSON string with category names
        """
        try:
            response = requests.get(f"{self.mcp_url}/reference/categories")
            return json.dumps({"categories": response.json().get("data", [])})
        except Exception as e:
            return json.dumps({"categories": [], "error": str(e)})


if __name__ == "__main__":
    from inspect import signature

    tool = Tools()
    sig = signature(tool.query_calendar)
    print("Function signature for query_calendar():")
    print(sig)

