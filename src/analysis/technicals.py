"""
Technical Analysis Engine

Calculates indicators for trading decisions:
- RSI (Relative Strength Index)
- Moving Averages (MA20, MA50, MA200)
- Support/Resistance levels
- Volume analysis
- Range position
"""

from typing import Dict, List, Tuple
import statistics


class TechnicalAnalysis:
    """
    Technical indicator calculations.

    All methods use only price/volume data (no external dependencies).
    """

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """
        Calculate RSI (Relative Strength Index).

        Args:
            prices: List of closing prices (newest first)
            period: RSI period (default 14)

        Returns:
            RSI value (0-100)
        """
        if len(prices) < period + 1:
            return 50.0  # Neutral if not enough data

        # Reverse to get oldest first
        prices = list(reversed(prices))

        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    @staticmethod
    def calculate_ma(prices: List[float], period: int) -> float:
        """
        Calculate Moving Average.

        Args:
            prices: List of closing prices (newest first)
            period: MA period (e.g., 20, 50, 200)

        Returns:
            Moving average value
        """
        if len(prices) < period:
            return prices[0] if prices else 0

        return statistics.mean(prices[:period])

    @staticmethod
    def calculate_support_resistance(candles: List[Dict]) -> Dict[str, float]:
        """
        Calculate support and resistance levels.

        Args:
            candles: List of OHLCV candles

        Returns:
            {"support": 100000, "resistance": 105000, "range_pct": 5.0}
        """
        if not candles:
            return {"support": 0, "resistance": 0, "range_pct": 0}

        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]

        resistance = max(highs)
        support = min(lows)

        range_pct = ((resistance - support) / support) * 100 if support > 0 else 0

        return {
            "support": round(support, 2),
            "resistance": round(resistance, 2),
            "range_pct": round(range_pct, 2)
        }

    @staticmethod
    def calculate_range_position(current_price: float, support: float, resistance: float) -> float:
        """
        Calculate where price is within range (0-100%).

        Args:
            current_price: Current price
            support: Support level
            resistance: Resistance level

        Returns:
            Position in range (0 = at support, 100 = at resistance)
        """
        if resistance <= support:
            return 50.0

        position = ((current_price - support) / (resistance - support)) * 100
        return max(0, min(100, round(position, 2)))

    @staticmethod
    def calculate_volume_ratio(candles: List[Dict]) -> float:
        """
        Calculate current volume vs average volume.

        Args:
            candles: List of OHLCV candles (newest first)

        Returns:
            Volume ratio (1.0 = average, 2.0 = 2x average)
        """
        if len(candles) < 2:
            return 1.0

        current_volume = candles[0]['volume']
        avg_volume = statistics.mean([c['volume'] for c in candles[1:21]])  # 20-period average

        if avg_volume == 0:
            return 1.0

        return round(current_volume / avg_volume, 2)

    @staticmethod
    def detect_trend(prices: List[float], short_period: int = 20, long_period: int = 50) -> Dict[str, any]:
        """
        Detect trend using MA crossover.

        Args:
            prices: List of closing prices (newest first)
            short_period: Short MA period
            long_period: Long MA period

        Returns:
            {"trend": "uptrend", "strength": "strong", "ma_short": 101000, "ma_long": 100000}
        """
        if len(prices) < long_period:
            return {"trend": "unknown", "strength": "weak", "ma_short": 0, "ma_long": 0}

        ma_short = TechnicalAnalysis.calculate_ma(prices, short_period)
        ma_long = TechnicalAnalysis.calculate_ma(prices, long_period)

        if ma_short > ma_long:
            diff_pct = ((ma_short - ma_long) / ma_long) * 100
            if diff_pct > 2:
                strength = "strong"
            elif diff_pct > 0.5:
                strength = "moderate"
            else:
                strength = "weak"
            trend = "uptrend"
        else:
            diff_pct = ((ma_long - ma_short) / ma_long) * 100
            if diff_pct > 2:
                strength = "strong"
            elif diff_pct > 0.5:
                strength = "moderate"
            else:
                strength = "weak"
            trend = "downtrend"

        return {
            "trend": trend,
            "strength": strength,
            "ma_short": round(ma_short, 2),
            "ma_long": round(ma_long, 2)
        }

    @classmethod
    def comprehensive_analysis(cls, candles: List[Dict], current_price: float) -> Dict:
        """
        Run all technical analyses.

        Args:
            candles: List of OHLCV candles (newest first)
            current_price: Current price

        Returns:
            Complete technical analysis
        """
        if not candles:
            return {"error": "No candle data"}

        prices = [c['close'] for c in candles]

        rsi = cls.calculate_rsi(prices)
        ma20 = cls.calculate_ma(prices, 20)
        ma50 = cls.calculate_ma(prices, 50)
        ma200 = cls.calculate_ma(prices, 200)

        sr_levels = cls.calculate_support_resistance(candles[:24])  # 24h range
        range_position = cls.calculate_range_position(
            current_price,
            sr_levels['support'],
            sr_levels['resistance']
        )

        volume_ratio = cls.calculate_volume_ratio(candles)
        trend = cls.detect_trend(prices)

        # Generate signals
        signals = []

        if rsi < 30:
            signals.append("RSI OVERSOLD - Potential buy")
        elif rsi > 70:
            signals.append("RSI OVERBOUGHT - Potential sell")

        if range_position < 20:
            signals.append("NEAR SUPPORT - Bounce opportunity")
        elif range_position > 80:
            signals.append("NEAR RESISTANCE - Take profit")

        if volume_ratio > 2.0:
            signals.append("HIGH VOLUME - Strong move confirmation")

        if trend['trend'] == 'uptrend' and trend['strength'] in ['strong', 'moderate']:
            signals.append("UPTREND - Follow the trend")
        elif trend['trend'] == 'downtrend' and trend['strength'] in ['strong', 'moderate']:
            signals.append("DOWNTREND - Avoid longs")

        return {
            "price": current_price,
            "indicators": {
                "rsi": rsi,
                "ma20": ma20,
                "ma50": ma50,
                "ma200": ma200,
                "volume_ratio": volume_ratio
            },
            "levels": sr_levels,
            "range_position": range_position,
            "trend": trend,
            "signals": signals
        }


if __name__ == "__main__":
    # Test with sample data
    print("📊 Testing Technical Analysis\n")

    # Sample candle data (BTC-like)
    sample_candles = [
        {"open": 101000, "high": 101500, "low": 100500, "close": 101200, "volume": 100},
        {"open": 100800, "high": 101200, "low": 100600, "close": 101000, "volume": 90},
        {"open": 100600, "high": 101000, "low": 100400, "close": 100800, "volume": 80},
    ] * 100  # Repeat for history

    analysis = TechnicalAnalysis.comprehensive_analysis(sample_candles, 101200)

    print("📈 Technical Analysis Results:")
    print(f"   Current Price: ${analysis['price']:,.2f}")
    print(f"\n📊 Indicators:")
    print(f"   RSI: {analysis['indicators']['rsi']}")
    print(f"   MA20: ${analysis['indicators']['ma20']:,.2f}")
    print(f"   MA50: ${analysis['indicators']['ma50']:,.2f}")
    print(f"   Volume Ratio: {analysis['indicators']['volume_ratio']}x")

    print(f"\n🎯 Levels:")
    print(f"   Support: ${analysis['levels']['support']:,.2f}")
    print(f"   Resistance: ${analysis['levels']['resistance']:,.2f}")
    print(f"   Range Position: {analysis['range_position']}%")

    print(f"\n📈 Trend:")
    print(f"   Direction: {analysis['trend']['trend']}")
    print(f"   Strength: {analysis['trend']['strength']}")

    print(f"\n⚡ Signals:")
    for signal in analysis['signals']:
        print(f"   • {signal}")

    print("\n✅ Technical analysis engine ready!")
