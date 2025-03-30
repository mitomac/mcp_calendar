import httpx
from dateutil.parser import isoparse

API_URL = "https://calendar.duke.edu/events/index.json?future_days=1"

def fetch_calendar_data():
    with httpx.Client(timeout=10) as client:
        resp = client.get(API_URL)
        resp.raise_for_status()
        return resp.json()

def validate_dates(events):
    bad_dates = []
    for event in events:
        for key in ['start_timestamp', 'end_timestamp']:
            date_value = event.get(key)
            if not date_value:
                bad_dates.append((event.get('id'), key, date_value, 'Missing or None'))
                continue
            try:
                isoparse(date_value)
            except Exception as e:
                bad_dates.append((event.get('id'), key, date_value, str(e)))
    return bad_dates

if __name__ == "__main__":
    data = fetch_calendar_data()
    events = data.get('events', []) if isinstance(data, dict) else data
    bad_dates = validate_dates(events)

    if bad_dates:
        print(f"Found {len(bad_dates)} problematic dates:")
        for event_id, key, val, reason in bad_dates:
            print(f"Event ID: {event_id}, Field: {key}, Value: {val}, Reason: {reason}")
    else:
        print("All timestamps are valid ISO8601 strings.")

