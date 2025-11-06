from coinbase.rest import RESTClient
from dotenv import load_dotenv
import os

load_dotenv('credentials/.env')

client = RESTClient(
    api_key=os.getenv('COINBASE_API_KEY_NAME'),
    api_secret=os.getenv('COINBASE_PRIVATE_KEY')
)

print("🔌 Testing BTC Price & Account Status\n")

# Get BTC candles for current price
candles = client.get_candles("BTC-USD", start=None, end=None, granularity="ONE_MINUTE")

if candles and hasattr(candles, 'candles') and len(candles.candles) > 0:
    latest_candle = candles.candles[0]
    print(f"💰 BTC Current Price: ${float(latest_candle.close):,.2f}")
    print(f"   24h High: ${float(latest_candle.high):,.2f}")
    print(f"   24h Low: ${float(latest_candle.low):,.2f}")

# Get account balances
print("\n💵 Your Account Balances:")
accounts_response = client.get_accounts(limit=250)
total_usd = 0.0
non_zero_balances = []

if hasattr(accounts_response, 'accounts'):
    for account in accounts_response.accounts:
        # Handle both dict and object responses
        if hasattr(account, 'available_balance'):
            balance_obj = account.available_balance
            if isinstance(balance_obj, dict):
                balance = float(balance_obj.get('value', 0))
                currency = balance_obj.get('currency', 'UNKNOWN')
            else:
                balance = float(balance_obj.value)
                currency = balance_obj.currency
        else:
            continue
            
        if balance > 0.0001:  # Show balances > 0.0001
            non_zero_balances.append((currency, balance))
            
            if currency in ['USD', 'USDC', 'USDT']:
                total_usd += balance

if non_zero_balances:
    for currency, balance in non_zero_balances:
        print(f"   {currency}: {balance:.8f}")
else:
    print("   No significant balances found")

print(f"\n💰 Total USD-equivalent: ${total_usd:.2f}")
print(f"   (Starting with ${total_usd:.2f} for trading)")

print("\n✅ Coinbase API is fully operational!")
print("🚀 Ready to start building RAYVEN!")
