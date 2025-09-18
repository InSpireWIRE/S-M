import os
from dotenv import load_dotenv
import httpx

load_dotenv('.env.development')
url = os.environ.get("SDP_SUPABASE_URL")
key = os.environ.get("SDP_SUPABASE_ANON_KEY")

print(f"Testing connection to: {url}")

try:
    response = httpx.get(f"{url}/rest/v1/", headers={"apikey": key})
    print(f"Status: {response.status_code}")
    print("Connection successful!")
except Exception as e:
    print(f"Error: {e}")
