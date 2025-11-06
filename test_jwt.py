import os
import time
import jwt
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

load_dotenv('credentials/.env')

api_key = os.getenv('COINBASE_API_KEY_NAME')
private_key_string = os.getenv('COINBASE_PRIVATE_KEY').replace('\\n', '\n')

print(f"API Key: {api_key[:50]}...")
print(f"Private Key starts with: {private_key_string[:30]}...")

# Load private key
private_key = serialization.load_pem_private_key(
    private_key_string.encode('utf-8'),
    password=None
)

# Generate JWT
current_time = int(time.time())
method = "GET"
path = "/api/v3/brokerage/accounts?limit=1"

payload = {
    'sub': api_key,
    'iss': 'coinbase-cloud',
    'nbf': current_time,
    'exp': current_time + 120,
    'aud': ['retail_rest_api_proxy'],
    'uri': f"{method} api.coinbase.com{path}"
}

print(f"\nPayload URI: {payload['uri']}")

token = jwt.encode(payload, private_key, algorithm='ES256')
print(f"\nJWT Token (first 50 chars): {token[:50]}...")
print(f"JWT Length: {len(token)}")

# Try to decode to verify
try:
    decoded = jwt.decode(token, options={"verify_signature": False})
    print(f"\nDecoded successfully:")
    print(f"  URI: {decoded['uri']}")
    print(f"  Sub: {decoded['sub'][:50]}...")
except Exception as e:
    print(f"Decode failed: {e}")
