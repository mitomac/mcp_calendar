# test_duke_calendar_api.py
import requests
import json
from datetime import datetime, timedelta
import pprint

def test_duke_calendar_api():
    # Duke Calendar API URL from your config
    api_url = "https://calendar.duke.edu/events/index.json"
    
    # Use today's date
    today = datetime.now().date()
    
    print(f"Fetching events for today: {today.isoformat()}")
    try:
        # Request parameters with feed_type=simple as in your code
        params = {
            "future_days": "0",  # Just today
            "feed_type": "simple"
        }
        
        # Make the request
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Print the top-level structure
        print("\nResponse structure:")
        if isinstance(data, dict):
            for key in data.keys():
                print(f"- {key}")
        else:
            print(f"Response is a {type(data).__name__}, length: {len(data)}")
        
        # Determine the events data
        if isinstance(data, dict) and "events" in data:
            events_data = data["events"]
        else:
            events_data = data
        
        print(f"\nFound {len(events_data)} events")
        
        if len(events_data) == 0:
            print("No events found for today. Trying with a broader date range...")
            
            # Try with a broader date range
            params["future_days"] = "7"  # Next 7 days
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, dict) and "events" in data:
                events_data = data["events"]
            else:
                events_data = data
            
            print(f"Found {len(events_data)} events for the next 7 days")
        
        # Extract all categories and groups
        categories = set()
        sponsors = set()
        
        for event in events_data:
            if "categories" in event and event["categories"]:
                categories.update(event["categories"])
            
            if "sponsor" in event and event["sponsor"]:
                sponsors.add(event["sponsor"])
        
        print(f"\nFound {len(categories)} unique categories")
        print(f"Found {len(sponsors)} unique sponsors")
        
        # Sample a few events
        sample_size = min(3, len(events_data))
        for i in range(sample_size):
            event = events_data[i]
            print(f"\n----- EVENT {i+1} -----")
            
            # Print key fields
            print("Key fields:")
            key_fields = ["id", "summary", "start_timestamp", "end_timestamp", 
                          "sponsor", "categories"]
            
            for field in key_fields:
                if field in event:
                    value = event[field]
                    print(f"{field}: {value}")
                else:
                    print(f"{field}: Not available")
            
            # Create a simplified event object
            print("\nSimplified event object:")
            simplified = {
                "id": event.get("id", ""),
                "title": event.get("summary", ""),
                "groups": event.get("sponsor", ""),
                "categories": event.get("categories", []) if event.get("categories") else [],
                "description": event.get("description", "")[:100] + "..." if event.get("description") and len(str(event.get("description"))) > 100 else event.get("description", ""),
                "start_time": event.get("start_timestamp", ""),
                "location": event.get("location", {}).get("address", "") if isinstance(event.get("location"), dict) else str(event.get("location", ""))
            }
            pprint.pprint(simplified)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_duke_calendar_api()
