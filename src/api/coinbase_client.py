"""
🔌 Coinbase Advanced Trade API Client

Secure client for Coinbase Advanced Trade API using JWT authentication.
All credentials loaded from environment variables (never hardcoded).
"""

import os
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
import jwt
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv


class CoinbaseClient:
    """
    Coinbase Advanced Trade API client with JWT authentication.

    Credentials loaded from .env file (never committed to git).
    """

    BASE_URL = "https://api.coinbase.com"

    def __init__(self, credentials_path: str = "credentials/.env"):
        """Initialize client with credentials from .env file"""

        # Load environment variables
        load_dotenv(credentials_path)

        self.api_key_name = os.getenv("COINBASE_API_KEY_NAME")
        private_key_string = os.getenv("COINBASE_PRIVATE_KEY")

        if not self.api_key_name or not private_key_string:
            raise ValueError(
                "Missing Coinbase credentials! "
                "Please set COINBASE_API_KEY_NAME and COINBASE_PRIVATE_KEY in credentials/.env"
            )

        # Clean up private key formatting
        private_key_string = private_key_string.replace("\\n", "\n")

        # Load private key for ECDSA signing (ES256)
        try:
            self.private_key = serialization.load_pem_private_key(
                private_key_string.encode('utf-8'),
                password=None
            )
        except Exception as e:
            raise ValueError(f"Invalid private key format: {e}")

        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "RAYVEN/1.0"
        })

    def _generate_jwt(self, method: str, path: str) -> str:
        """
        Generate JWT token for authentication.

        Uses ES256 (ECDSA with SHA-256) algorithm.
        Tokens expire after 2 minutes.
        """
        current_time = int(time.time())

        payload = {
            "sub": self.api_key_name,
            "iss": "coinbase-cloud",
            "nbf": current_time,
            "exp": current_time + 120,  # 2 minute expiry
            "aud": ["retail_rest_api_proxy"],
            "uri": f"{method} {self.BASE_URL.replace('https://', '')}{path}"
        }

        token = jwt.encode(payload, self.private_key, algorithm="ES256")
        return token

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Coinbase API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path (must include query params if needed)
            data: Request body (for POST/PUT)

        Returns:
            Response JSON as dictionary
        """
        url = f"{self.BASE_URL}{path}"

        # Generate fresh JWT for this request
        token = self._generate_jwt(method, path)

        headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
            except:
                error_detail = e.response.text

            raise Exception(f"Coinbase API Error: {e}\nDetails: {error_detail}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    # ==================== ACCOUNT METHODS ====================

    def get_accounts(self, limit: int = 250) -> List[Dict]:
        """
        Get all account balances.

        IMPORTANT: Use limit=250 to ensure USD account is included
        (it's often in account #50+)
        """
        response = self._request(
            "GET",
            f"/api/v3/brokerage/accounts?limit={limit}"
        )
        return response.get("accounts", [])

    def get_balances(self) -> Dict[str, float]:
        """
        Get simplified balance dictionary.

        Returns:
            {"USD": 60.0, "BTC": 0.00012, "ETH": 0.05, ...}
        """
        accounts = self.get_accounts(limit=250)
        balances = {}

        for account in accounts:
            currency = account.get("currency", "")
            available = float(account.get("available_balance", {}).get("value", 0))

            if available > 0.01:  # Only include significant balances
                balances[currency] = available

        return balances

    def get_usd_balance(self) -> float:
        """Get available USD balance"""
        balances = self.get_balances()
        return balances.get("USD", 0.0) + balances.get("USDC", 0.0) + balances.get("USDT", 0.0)

    # ==================== MARKET DATA METHODS ====================

    def get_product(self, product_id: str) -> Dict:
        """Get product details (e.g., 'BTC-USD')"""
        return self._request("GET", f"/api/v3/brokerage/products/{product_id}")

    def get_ticker(self, product_id: str) -> Dict:
        """
        Get current price and 24h stats.

        Returns:
            {
                "price": "43850.00",
                "volume_24h": "28500000000",
                "price_change_24h": "2.5",
                ...
            }
        """
        path = f"/api/v3/brokerage/products/{product_id}/ticker"
        return self._request("GET", path)

    def get_candles(
        self,
        product_id: str,
        granularity: str = "FIVE_MINUTE",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get historical candles (OHLCV data).

        Args:
            product_id: e.g., 'BTC-USD'
            granularity: ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, ONE_HOUR, ONE_DAY
            start: Start time (default: 24 hours ago)
            end: End time (default: now)

        Returns:
            List of candles [{start, low, high, open, close, volume}, ...]
        """
        if not start:
            start = datetime.now() - timedelta(hours=24)
        if not end:
            end = datetime.now()

        path = f"/api/v3/brokerage/products/{product_id}/candles?granularity={granularity}&start={int(start.timestamp())}&end={int(end.timestamp())}"

        response = self._request("GET", path)

        return response.get("candles", [])

    # ==================== TRADING METHODS ====================

    def create_market_order(
        self,
        product_id: str,
        side: str,  # "BUY" or "SELL"
        size: Optional[str] = None,  # Amount of base currency
        funds: Optional[str] = None,  # Amount of quote currency (USD)
        client_order_id: Optional[str] = None
    ) -> Dict:
        """
        Create a market order.

        Args:
            product_id: e.g., 'BTC-USD'
            side: 'BUY' or 'SELL'
            size: Amount of BTC to buy/sell (e.g., '0.001')
            funds: Amount of USD to spend (e.g., '50.00') - used for buys
            client_order_id: Optional unique ID for idempotency

        Returns:
            Order response with order_id, status, etc.
        """
        if not size and not funds:
            raise ValueError("Must specify either size or funds")

        order_config = {
            "market_market_ioc": {}
        }

        if size:
            order_config["market_market_ioc"]["base_size"] = str(size)
        if funds:
            order_config["market_market_ioc"]["quote_size"] = str(funds)

        data = {
            "product_id": product_id,
            "side": side.upper(),
            "order_configuration": order_config
        }

        if client_order_id:
            data["client_order_id"] = client_order_id

        return self._request("POST", "/api/v3/brokerage/orders", data=data)

    def get_order(self, order_id: str) -> Dict:
        """Get order details by ID"""
        return self._request("GET", f"/api/v3/brokerage/orders/historical/{order_id}")

    def get_fills(self, product_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Get fill history (executed trades).

        Used for accurate P&L calculation based on real entry prices.
        """
        path = f"/api/v3/brokerage/orders/historical/fills?limit={limit}"
        if product_id:
            path += f"&product_id={product_id}"

        response = self._request("GET", path)

        return response.get("fills", [])

    # ==================== HELPER METHODS ====================

    def get_current_price(self, product_id: str) -> float:
        """Get current price as float"""
        ticker = self.get_ticker(product_id)
        return float(ticker.get("price", 0))

    def get_24h_stats(self, product_id: str) -> Dict[str, float]:
        """
        Get 24-hour statistics.

        Returns:
            {
                "price": 43850.00,
                "volume": 28500000000.0,
                "high": 44500.00,
                "low": 43200.00,
                "change_percent": 2.5
            }
        """
        ticker = self.get_ticker(product_id)

        return {
            "price": float(ticker.get("price", 0)),
            "volume": float(ticker.get("volume_24h", 0)),
            "high": float(ticker.get("high_24h", 0)),
            "low": float(ticker.get("low_24h", 0)),
            "change_percent": float(ticker.get("price_percentage_change_24h", 0))
        }

    def health_check(self) -> bool:
        """Test API connectivity and credentials"""
        try:
            self.get_accounts(limit=1)
            return True
        except Exception as e:
            print(f"Health check failed: {e}")
            return False


if __name__ == "__main__":
    # Test the client (credentials loaded from .env)
    print("🔌 Testing Coinbase API Client\n")

    try:
        client = CoinbaseClient()

        print("✅ Credentials loaded successfully")
        print("\n🔍 Running health check...")

        if client.health_check():
            print("✅ API connection successful\n")

            print("💰 Account Balances:")
            balances = client.get_balances()
            for currency, amount in balances.items():
                print(f"  {currency}: {amount:.8f}")

            print(f"\n💵 Total USD: ${client.get_usd_balance():.2f}")

            print("\n📊 BTC Current Stats:")
            stats = client.get_24h_stats("BTC-USD")
            print(f"  Price: ${stats['price']:,.2f}")
            print(f"  24h High: ${stats['high']:,.2f}")
            print(f"  24h Low: ${stats['low']:,.2f}")
            print(f"  24h Change: {stats['change_percent']:+.2f}%")
            print(f"  24h Volume: ${stats['volume']:,.0f}")

        else:
            print("❌ API connection failed")

    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n📝 Please ensure credentials/.env file exists with:")
        print("   - COINBASE_API_KEY_NAME")
        print("   - COINBASE_PRIVATE_KEY")
    except Exception as e:
        print(f"❌ Error: {e}")
