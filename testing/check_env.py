import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DUKE_DIRECTORY_API_KEY")
print(f"API key loaded: {api_key}")
