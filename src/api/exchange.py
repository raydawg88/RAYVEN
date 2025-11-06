"""
Coinbase API Wrapper

Clean interface for trading operations using official Coinbase SDK.
All credentials loaded from environment (never hardcoded).
"""

import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from coinbase.rest import RESTClient
from dotenv import load_dotenv


class CoinbaseAPI:
    """
    Wrapper around Coinbase official SDK.

    Provides clean methods for:
    - Account balances
    - Market data (prices, candles)
    - Trading (buy/sell)
    """

    def __init__(self, credentials_path: str = "credentials/.env"):
        load_dotenv(credentials_path)

        self.api_key = os.getenv("COINBASE_API_KEY_NAME")
        self.api_secret = os.getenv("COINBASE_PRIVATE_KEY")

        if not self.api_key or not self.api_secret:
            raise ValueError("Missing Coinbase credentials in .env file")

        self.client = RESTClient(
            api_key=self.api_key,
            api_secret=self.api_secret
        )

    # ==================== ACCOUNT METHODS ====================

    def get_total_balance_usd(self) -> float:
        """
        Get total USD-equivalent balance.

        Includes:
        - USD, USDC, USDT (as USD)
        - BTC, ETH, XRP, etc. (converted to USD at current price)

        Returns:
            Total balance in USD
        """
        accounts = self.client.get_accounts(limit=250)
        total_usd = 0.0

        if not hasattr(accounts, 'accounts'):
            return 0.0

        for account in accounts.accounts:
            if not hasattr(account, 'available_balance'):
                continue

            balance_obj = account.available_balance
            if isinstance(balance_obj, dict):
                balance = float(balance_obj.get('value', 0))
                currency = balance_obj.get('currency', '')
            else:
                balance = float(balance_obj.value)
                currency = balance_obj.currency

            if balance < 0.00000001:  # Skip dust
                continue

            # Direct USD
            if currency in ['USD', 'USDC', 'USDT']:
                total_usd += balance
            # Convert crypto to USD
            else:
                try:
                    price = self.get_current_price(f"{currency}-USD")
                    total_usd += balance * price
                except:
                    pass  # Skip if can't get price

        return total_usd

    def get_balances(self) -> Dict[str, float]:
        """
        Get all non-zero balances.

        Returns:
            {"BTC": 0.00025, "XRP": 15.36, "USDC": 0.007, ...}
        """
        accounts = self.client.get_accounts(limit=250)
        balances = {}

        if not hasattr(accounts, 'accounts'):
            return {}

        for account in accounts.accounts:
            if not hasattr(account, 'available_balance'):
                continue

            balance_obj = account.available_balance
            if isinstance(balance_obj, dict):
                balance = float(balance_obj.get('value', 0))
                currency = balance_obj.get('currency', '')
            else:
                balance = float(balance_obj.value)
                currency = balance_obj.currency

            if balance > 0.00000001:  # Skip dust
                balances[currency] = balance

        return balances

    # ==================== MARKET DATA METHODS ====================

    def get_current_price(self, product_id: str) -> float:
        """
        Get current price for a product.

        Args:
            product_id: e.g., "BTC-USD"

        Returns:
            Current price as float
        """
        candles = self.client.get_candles(
            product_id=product_id,
            start=None,
            end=None,
            granularity="ONE_MINUTE"
        )

        if candles and hasattr(candles, 'candles') and len(candles.candles) > 0:
            return float(candles.candles[0].close)

        raise Exception(f"Could not fetch price for {product_id}")

    def get_ohlcv(self, product_id: str, granularity: str = "FIVE_MINUTE", count: int = 100) -> List[Dict]:
        """
        Get OHLCV candle data.

        Args:
            product_id: e.g., "BTC-USD"
            granularity: ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, ONE_HOUR, ONE_DAY
            count: Number of candles to fetch

        Returns:
            List of candles: [{open, high, low, close, volume, start}, ...]
        """
        candles = self.client.get_candles(
            product_id=product_id,
            start=None,
            end=None,
            granularity=granularity
        )

        if not candles or not hasattr(candles, 'candles'):
            return []

        result = []
        for candle in candles.candles[:count]:
            result.append({
                'start': candle.start,
                'open': float(candle.open),
                'high': float(candle.high),
                'low': float(candle.low),
                'close': float(candle.close),
                'volume': float(candle.volume)
            })

        return result

    def get_24h_stats(self, product_id: str) -> Dict[str, float]:
        """
        Get 24-hour statistics.

        Returns:
            {
                "current": 101284.47,
                "high": 102500.00,
                "low": 99800.00,
                "volume": 2500.5,
                "change_percent": 2.5
            }
        """
        candles = self.get_ohlcv(product_id, granularity="ONE_HOUR", count=24)

        if not candles:
            raise Exception(f"Could not fetch 24h stats for {product_id}")

        current = candles[0]['close']
        high_24h = max(c['high'] for c in candles)
        low_24h = min(c['low'] for c in candles)
        volume_24h = sum(c['volume'] for c in candles)

        open_24h = candles[-1]['open']
        change_percent = ((current - open_24h) / open_24h) * 100 if open_24h > 0 else 0

        return {
            'current': current,
            'high': high_24h,
            'low': low_24h,
            'volume': volume_24h,
            'change_percent': change_percent
        }

    # ==================== TRADING METHODS ====================

    def buy_market(self, product_id: str, usd_amount: float) -> Dict:
        """
        Buy crypto with USD (market order).

        Args:
            product_id: e.g., "BTC-USD"
            usd_amount: How much USD to spend (e.g., 15.00)

        Returns:
            Order details
        """
        # Create market order
        order = self.client.market_order_buy(
            client_order_id=self._generate_order_id(),
            product_id=product_id,
            quote_size=str(usd_amount)
        )

        return self._parse_order_response(order)

    def sell_market(self, product_id: str, crypto_amount: float) -> Dict:
        """
        Sell crypto for USD (market order).

        Args:
            product_id: e.g., "BTC-USD"
            crypto_amount: How much crypto to sell (e.g., 0.001)

        Returns:
            Order details
        """
        order = self.client.market_order_sell(
            client_order_id=self._generate_order_id(),
            product_id=product_id,
            base_size=str(crypto_amount)
        )

        return self._parse_order_response(order)

    # ==================== HELPER METHODS ====================

    def _generate_order_id(self) -> str:
        """Generate unique order ID"""
        import uuid
        return str(uuid.uuid4())

    def _parse_order_response(self, order) -> Dict:
        """Parse order response into clean dict"""
        if hasattr(order, 'success') and order.success:
            return {
                'success': True,
                'order_id': getattr(order, 'order_id', None),
                'status': getattr(order, 'status', 'unknown')
            }
        else:
            return {
                'success': False,
                'error': str(order)
            }

    def health_check(self) -> bool:
        """Test API connectivity"""
        try:
            self.client.get_accounts(limit=1)
            return True
        except:
            return False


if __name__ == "__main__":
    # Test the API
    print("🔌 Testing Coinbase API Wrapper\n")

    api = CoinbaseAPI()

    print("✅ API initialized")
    print(f"✅ Health check: {api.health_check()}")

    print("\n💰 Account Status:")
    balances = api.get_balances()
    for currency, amount in balances.items():
        print(f"   {currency}: {amount:.8f}")

    total = api.get_total_balance_usd()
    print(f"\n💵 Total Value: ${total:.2f}")

    print("\n📊 BTC Market Data:")
    price = api.get_current_price("BTC-USD")
    print(f"   Current Price: ${price:,.2f}")

    stats = api.get_24h_stats("BTC-USD")
    print(f"   24h High: ${stats['high']:,.2f}")
    print(f"   24h Low: ${stats['low']:,.2f}")
    print(f"   24h Change: {stats['change_percent']:+.2f}%")

    print("\n✅ Coinbase API wrapper is ready!")
