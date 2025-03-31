import httpx

API_URL = "https://calendar.duke.edu/events/index.json?future_days=1"

def fetch_and_print_sample(n=3):
    with httpx.Client(timeout=10) as client:
        resp = client.get(API_URL)
        resp.raise_for_status()
        data = resp.json()
        events = data.get('events', []) if isinstance(data, dict) else data
        print(events[:n])

if __name__ == "__main__":
    fetch_and_print_sample()

