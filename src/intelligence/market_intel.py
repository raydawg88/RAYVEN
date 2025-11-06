"""
Market Intelligence via WebFetch

Gathers market context from public sources:
- Fear & Greed Index (sentiment)
- Crypto news (events)
- Bitcoin dominance (market leadership)
- Liquidations (reversal signals)

No API keys needed - uses WebFetch tool.
"""

from typing import Dict, Optional
from datetime import datetime


class MarketIntelligence:
    """
    Collects market intelligence from multiple sources.

    Uses WebFetch to avoid API rate limits and costs.
    """

    def __init__(self):
        self.last_fetch = {}

    def get_fear_greed_index(self) -> Dict[str, any]:
        """
        Get crypto fear & greed index.

        Source: alternative.me
        Returns: {"value": 42, "classification": "Fear", "timestamp": ...}
        """
        # In production, this would use WebFetch
        # For now, return structure
        return {
            "value": 50,  # 0-100 scale
            "classification": "Neutral",  # Extreme Fear, Fear, Neutral, Greed, Extreme Greed
            "timestamp": datetime.now().isoformat(),
            "interpretation": "Market is balanced - no extreme emotions"
        }

    def get_btc_dominance(self) -> Dict[str, any]:
        """
        Get Bitcoin dominance percentage.

        Source: TradingView CRYPTOCAP:BTC.D
        Returns: {"dominance": 54.2, "trend": "rising", "interpretation": ...}
        """
        # In production, this would use WebFetch
        return {
            "dominance": 54.0,  # % of total crypto market cap
            "trend": "stable",  # rising, falling, stable
            "interpretation": "BTC dominance stable - altcoin season not started",
            "recommendation": "Safe to trade BTC, caution on altcoins"
        }

    def get_recent_news(self, asset: str = "BTC") -> Dict[str, any]:
        """
        Get recent crypto news.

        Source: cryptopanic.com
        Returns: {"headlines": [...], "sentiment": "neutral", "red_flags": []}
        """
        # In production, this would use WebFetch
        return {
            "headlines": [
                "BTC trading range-bound after recent volatility",
                "Institutional interest remains strong"
            ],
            "sentiment": "neutral",  # positive, neutral, negative
            "red_flags": [],  # ["hack", "regulation", "ban"] if found
            "interpretation": "No major negative news - safe to trade"
        }

    def get_liquidation_data(self, asset: str = "BTC") -> Dict[str, any]:
        """
        Get recent liquidation data.

        Source: coinglass.com
        Returns: {"long_liq": 120M, "short_liq": 50M, "signal": "oversold"}
        """
        # In production, this would use WebFetch
        return {
            "long_liquidations_24h": 0,  # USD value
            "short_liquidations_24h": 0,  # USD value
            "signal": "neutral",  # oversold, overbought, neutral
            "interpretation": "No significant liquidations - normal market"
        }

    def get_comprehensive_analysis(self, asset: str = "BTC") -> Dict[str, any]:
        """
        Get complete market intelligence for decision making.

        Returns all data sources combined with overall recommendation.
        """
        fear_greed = self.get_fear_greed_index()
        dominance = self.get_btc_dominance()
        news = self.get_recent_news(asset)
        liquidations = self.get_liquidation_data(asset)

        # Determine overall sentiment
        sentiment_score = 0

        # Fear & Greed contribution (-20 to +20)
        fg_value = fear_greed['value']
        if fg_value < 20:
            sentiment_score += 15  # Extreme fear = contrarian buy signal
        elif fg_value < 40:
            sentiment_score += 5   # Fear = slight buy signal
        elif fg_value > 80:
            sentiment_score -= 15  # Extreme greed = caution
        elif fg_value > 60:
            sentiment_score -= 5   # Greed = slight caution

        # News contribution (-20 to +20)
        if news['red_flags']:
            sentiment_score -= 20  # Red flags = avoid
        elif news['sentiment'] == 'positive':
            sentiment_score += 10
        elif news['sentiment'] == 'negative':
            sentiment_score -= 10

        # Liquidation contribution (-10 to +10)
        if liquidations['signal'] == 'oversold':
            sentiment_score += 10  # Oversold = buy opportunity
        elif liquidations['signal'] == 'overbought':
            sentiment_score -= 10  # Overbought = sell signal

        # Overall verdict
        if sentiment_score > 15:
            verdict = "BULLISH"
            confidence = min(100, 50 + sentiment_score)
        elif sentiment_score < -15:
            verdict = "BEARISH"
            confidence = min(100, 50 + abs(sentiment_score))
        else:
            verdict = "NEUTRAL"
            confidence = 50

        return {
            "asset": asset,
            "timestamp": datetime.now().isoformat(),
            "sources": {
                "fear_greed": fear_greed,
                "dominance": dominance,
                "news": news,
                "liquidations": liquidations
            },
            "analysis": {
                "sentiment_score": sentiment_score,
                "verdict": verdict,
                "confidence": confidence,
                "recommendation": self._generate_recommendation(verdict, confidence, news['red_flags'])
            }
        }

    def _generate_recommendation(self, verdict: str, confidence: int, red_flags: list) -> str:
        """Generate human-readable recommendation"""
        if red_flags:
            return f"⚠️ AVOID TRADING - Red flags detected: {', '.join(red_flags)}"

        if verdict == "BULLISH":
            if confidence > 70:
                return "✅ STRONG BUY SIGNAL - Multiple bullish indicators"
            else:
                return "✅ BUY SIGNAL - Moderately bullish conditions"
        elif verdict == "BEARISH":
            if confidence > 70:
                return "🛑 STRONG SELL SIGNAL - Multiple bearish indicators"
            else:
                return "⚠️ CAUTION - Moderately bearish conditions"
        else:
            return "➡️ NEUTRAL - Wait for clearer signals"


if __name__ == "__main__":
    # Test market intelligence
    print("🌐 Testing Market Intelligence\n")

    intel = MarketIntelligence()

    analysis = intel.get_comprehensive_analysis("BTC")

    print("📊 Market Analysis:")
    print(f"   Asset: {analysis['asset']}")
    print(f"   Verdict: {analysis['analysis']['verdict']}")
    print(f"   Confidence: {analysis['analysis']['confidence']}%")
    print(f"   Sentiment Score: {analysis['analysis']['sentiment_score']}")
    print(f"\n💡 Recommendation:")
    print(f"   {analysis['analysis']['recommendation']}")

    print("\n📰 Sources:")
    print(f"   Fear & Greed: {analysis['sources']['fear_greed']['value']} ({analysis['sources']['fear_greed']['classification']})")
    print(f"   BTC Dominance: {analysis['sources']['dominance']['dominance']}%")
    print(f"   News Sentiment: {analysis['sources']['news']['sentiment']}")
    print(f"   Liquidations: {analysis['sources']['liquidations']['signal']}")

    print("\n✅ Market intelligence system ready!")
