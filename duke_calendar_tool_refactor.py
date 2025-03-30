"""
title: Duke Calendar Tool
author: Claude
author_url: https://www.anthropic.com
description: A tool for querying Duke University calendar events using natural language.
version: 1.0.0
license: MIT
required_open_webui_version: 0.4.0
requirements: requests

USAGE INSTRUCTIONS FOR LLM:
This tool helps you find and present events from Duke University's calendar based on natural language queries.

FOLLOW THESE EXACT STEPS WHEN ANSWERING CALENDAR QUERIES:
1. CONVERT TIME TO DATES: Use parse_date_range() to convert expressions like "today", "this weekend" into ISO format dates.
   Example: parse_date_range("this weekend") → {"start_date": "2025-04-05", "end_date": "2025-04-06"}

2. GET SIMPLIFIED EVENTS: Use get_simplified_events() with the date range to retrieve events.
   Each event will have a local_id and essential details (title, categories, etc.)

3. ANALYZE & SELECT EVENTS: Examine the simplified events to find matches for the query.
   Look at titles, descriptions, categories, and groups (sponsors) to find relevant events.

4. GATHER ALL RELEVANT IDs: Collect all relevant local_ids into a SINGLE comma-separated list.
   IMPORTANT: Always batch multiple IDs into ONE call rather than making separate calls for each ID.
   Example: "9,12,13" NOT separate calls for 9, then 12, then 13.

5. GET FULL DETAILS IN ONE CALL: Use get_events_by_local_ids() with your comma-separated list.
   Example: get_events_by_local_ids("9,12,13")

6. PRESENT RESULTS APPROPRIATELY:
   - For a small number of events (1-5): Present each one with formatted details
   - For many events: Group by day or category, highlight 3-5 standout events, and offer filtering suggestions
   - For specific queries (e.g., "piano concerts"): Focus on the most relevant matches
   - Always present events chronologically when possible

HANDLING LARGE RESULT SETS:
If a query would return many events (e.g., "what's happening this week"):
1. Categorize and summarize (e.g., "15 arts events, 8 lectures...")
2. Highlight a few diverse, notable events
3. Group by day of the week
4. Offer to narrow the search ("Would you like to focus on weekend events?")
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class Tools:
    def __init__(self):
        self.citation = True
        self.mcp_url = "http://macalpine.colab.duke.edu:8000/api/v1/calendar"  # URL to the MCP server

    def parse_date_range(self, time_expression: str) -> str:
        """
        Convert a natural language time expression to a date range.

        :param time_expression: Natural language time expression (e.g., "today", "next week")
        :return: JSON string with start_date and end_date in ISO format
        """
        today = datetime.now().date()

        # Default to today
        start_date = today
        end_date = today

        # Parse common time expressions
        time_expression = time_expression.lower()

        if "today" in time_expression:
            pass  # Already set to today
        elif "tomorrow" in time_expression:
            start_date = today + timedelta(days=1)
            end_date = start_date
        elif "this week" in time_expression:
            # Start from today, end on Sunday
            days_to_sunday = 6 - today.weekday()
            end_date = today + timedelta(days=days_to_sunday)
        elif "next week" in time_expression:
            # Start next Monday, end next Sunday
            days_to_monday = (7 - today.weekday()) % 7
            if days_to_monday == 0:
                days_to_monday = 7
            start_date = today + timedelta(days=days_to_monday)
            end_date = start_date + timedelta(days=6)
        elif "weekend" in time_expression or "this weekend" in time_expression:
            # Saturday and Sunday
            days_to_saturday = (5 - today.weekday()) % 7
            if days_to_saturday == 0 and today.weekday() != 5:  # Not already Saturday
                days_to_saturday = 7
            start_date = today + timedelta(days=days_to_saturday)
            end_date = start_date + timedelta(days=1)
        elif "next weekend" in time_expression:
            # Next Saturday and Sunday
            days_to_saturday = (5 - today.weekday()) % 7
            if days_to_saturday == 0:  # Today is Saturday
                days_to_saturday = 7
            start_date = today + timedelta(days=days_to_saturday + 7)
            end_date = start_date + timedelta(days=1)
        elif "next month" in time_expression:
            # Start of next month
            if today.month == 12:
                start_date = today.replace(year=today.year + 1, month=1, day=1)
            else:
                start_date = today.replace(month=today.month + 1, day=1)

            # End of next month
            if start_date.month == 12:
                end_date = start_date.replace(
                    year=start_date.year + 1, month=1, day=1
                ) - timedelta(days=1)
            else:
                end_date = start_date.replace(
                    month=start_date.month + 1, day=1
                ) - timedelta(days=1)
        elif "this month" in time_expression:
            # From today to end of month
            if today.month == 12:
                end_date = today.replace(
                    year=today.year + 1, month=1, day=1
                ) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(
                    days=1
                )

        return json.dumps(
            {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "time_expression": time_expression,
            }
        )

    def get_simplified_events(self, start_date: str, end_date: str) -> str:
        """
        Retrieve simplified events for a specific date range.

        :param start_date: Start date in ISO format (YYYY-MM-DD)
        :param end_date: End date in ISO format (YYYY-MM-DD)
        :return: JSON string with simplified event data for analysis
        """
        try:
            response = requests.get(
                f"{self.mcp_url}/simplified-events",
                params={"start_date": start_date, "end_date": end_date},
            )
            response.raise_for_status()

            return response.text
        except Exception as e:
            return json.dumps(
                {"error": f"Error fetching simplified events: {str(e)}", "events": []}
            )

    def get_events_by_local_ids(self, local_ids: str) -> str:
        """
        Get full event details using local IDs.

        :param local_ids: Comma-separated list of local event IDs (e.g., "1,5,9")
        :return: JSON string with full event details
        """
        try:
            # Parse comma-separated local IDs
            id_list = [int(id.strip()) for id in local_ids.split(",") if id.strip()]

            # Get event details
            response = requests.post(
                f"{self.mcp_url}/events-by-local-ids", json={"local_ids": id_list}
            )
            response.raise_for_status()

            return response.text
        except Exception as e:
            return json.dumps(
                {"error": f"Error fetching events by local IDs: {str(e)}", "events": []}
            )


if __name__ == "__main__":
    print("Calendar tool initialized")

