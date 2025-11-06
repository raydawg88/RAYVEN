from coinbase.rest import RESTClient
from dotenv import load_dotenv
import os

load_dotenv('credentials/.env')

api_key = os.getenv('COINBASE_API_KEY_NAME')
private_key = os.getenv('COINBASE_PRIVATE_KEY')

print("🔌 Testing Official Coinbase SDK\n")

try:
    client = RESTClient(api_key=api_key, api_secret=private_key)
    
    print("✅ Client created successfully")
    print("\n📡 Testing accounts endpoint...")
    
    accounts = client.get_accounts()
    
    print(f"✅ SUCCESS! Got response")
    print(f"Accounts data: {accounts}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e)}")
