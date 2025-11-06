import os
from dotenv import load_dotenv

load_dotenv('credentials/.env')

api_key = os.getenv('COINBASE_API_KEY_NAME')
private_key = os.getenv('COINBASE_PRIVATE_KEY')

print("🔍 Checking API Key Format\n")
print("=" * 60)

# Check API key format
print(f"API Key Name: {api_key}")
print(f"Format check:")
if api_key.startswith('organizations/') and '/apiKeys/' in api_key:
    print("  ✅ Correct format (organizations/.../apiKeys/...)")
else:
    print("  ❌ Wrong format - should be organizations/.../apiKeys/...")

# Check private key format  
print(f"\nPrivate Key:")
if '\\n' in private_key:
    print("  ⚠️  Contains literal \\n (will be converted)")
    private_key = private_key.replace('\\n', '\n')
    
if private_key.startswith('-----BEGIN EC PRIVATE KEY-----'):
    print("  ✅ Starts with correct header")
else:
    print(f"  ❌ Wrong start: {private_key[:30]}")
    
if '-----END EC PRIVATE KEY-----' in private_key:
    print("  ✅ Has correct footer")
else:
    print("  ❌ Missing footer")

lines = private_key.split('\n')
print(f"  Lines in key: {len(lines)}")
if len(lines) >= 5:
    print("  ✅ Reasonable number of lines")
else:
    print("  ❌ Too few lines")

print("\n" + "=" * 60)
print("\n🎯 NEXT STEPS TO CHECK:")
print("\n1. Go to: https://portal.cdp.coinbase.com/projects")
print("2. Click on your project")
print("3. Click 'API Keys' in left menu")
print("4. Find your key: ...f68029211")
print("\n5. VERIFY THESE SETTINGS:")
print("   ✅ Status: ACTIVE (not pending/disabled)")
print("   ✅ Permissions: Should include:")
print("      - wallet:accounts:read")
print("      - wallet:buys:create")
print("      - wallet:sells:create")
print("      - wallet:trades:read")
print("   ⚠️  IP Restrictions: NONE (or includes your current IP)")
print("\n6. If any are wrong, either:")
print("   a) Edit the key to fix permissions")
print("   b) Delete it and create a new one with correct settings")
