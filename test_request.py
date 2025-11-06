import os
import time
import requests
import jwt
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

load_dotenv('credentials/.env')

api_key = os.getenv('COINBASE_API_KEY_NAME')
private_key_string = os.getenv('COINBASE_PRIVATE_KEY').replace('\\n', '\n')

private_key = serialization.load_pem_private_key(
    private_key_string.encode('utf-8'),
    password=None
)

method = "GET"
path = "/api/v3/brokerage/accounts?limit=1"
current_time = int(time.time())

payload = {
    'sub': api_key,
    'iss': 'coinbase-cloud',
    'nbf': current_time,
    'exp': current_time + 120,
    'aud': ['retail_rest_api_proxy'],
    'uri': f"{method} api.coinbase.com{path}"
}

token = jwt.encode(payload, private_key, algorithm='ES256')

url = f"https://api.coinbase.com{path}"
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

print(f"Making request to: {url}")
print(f"Authorization header: Bearer {token[:30]}...")

response = requests.get(url, headers=headers)
print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text[:500]}")
