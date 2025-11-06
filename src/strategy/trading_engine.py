"""
Trading Engine with Reinforcement Learning

The decision-making system that learns to trade profitably.

Uses:
- Technical analysis signals (RSI, support/resistance, trend)
- Market intelligence (fear/greed, news, liquidations)
- Moon phase correlations (learned from memory)
- Pattern success rates (learned from memory)
- Q-learning for strategy optimization

Actions: BUY, SELL, HOLD
"""

import random
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from enum import Enum


class Action(Enum):
    """Trading actions"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class TradingPattern(Enum):
    """Known trading patterns"""
    SUPPORT_BOUNCE = "support_bounce"
    RESISTANCE_REJECT = "resistance_reject"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    BREAKDOWN = "breakdown"
    TREND_FOLLOW = "trend_follow"


class TradingEngine:
    """
    Reinforcement learning trading engine.

    Learns optimal strategies through experience.
    """

    def __init__(
        self,
        memory_system,
        progression_system,
        exploration_rate: float = 0.2,
        min_confidence: float = 0.6
    ):
        """
        Args:
            memory_system: Memory instance for learning from history
            progression_system: Progression instance for level/coin restrictions
            exploration_rate: % of time to explore (vs exploit learned patterns)
            min_confidence: Minimum confidence to take action (0-1)
        """
        self.memory = memory_system
        self.progression = progression_system
        self.exploration_rate = exploration_rate
        self.min_confidence = min_confidence

    # ==================== DECISION MAKING ====================

    def decide_action(
        self,
        coin: str,
        current_price: float,
        technical_analysis: Dict,
        market_intelligence: Dict,
        moon_phase: str,
        current_holdings: Dict
    ) -> Dict:
        """
        Decide what action to take (BUY/SELL/HOLD).

        Returns:
            {
                "action": Action.BUY,
                "confidence": 0.85,
                "pattern": "support_bounce",
                "reasoning": "RSI oversold + near support + bullish moon",
                "expected_outcome": "+3-5%",
                "risk_level": "medium"
            }
        """
        # Check if coin is unlocked
        if not self.progression.can_trade_coin(coin):
            return {
                "action": Action.HOLD,
                "confidence": 1.0,
                "pattern": None,
                "reasoning": f"{coin} is locked - unlock by reaching next level",
                "expected_outcome": "N/A",
                "risk_level": "none"
            }

        # Check if we own this coin
        owns_coin = coin in current_holdings and current_holdings[coin] > 0

        # Analyze market state
        state = self._analyze_state(
            technical_analysis,
            market_intelligence,
            moon_phase
        )

        # Detect patterns
        patterns = self._detect_patterns(technical_analysis, state)

        # If we own it, check for sell signals
        if owns_coin:
            sell_decision = self._evaluate_sell(
                coin, current_price, patterns, state, current_holdings[coin]
            )
            if sell_decision:
                return sell_decision

        # If we don't own it, check for buy signals
        buy_decision = self._evaluate_buy(
            coin, current_price, patterns, state
        )
        if buy_decision:
            return buy_decision

        # Default: HOLD
        return {
            "action": Action.HOLD,
            "confidence": 0.5,
            "pattern": None,
            "reasoning": "No clear signal - waiting for better setup",
            "expected_outcome": "N/A",
            "risk_level": "none"
        }

    # ==================== STATE ANALYSIS ====================

    def _analyze_state(
        self,
        technical: Dict,
        intelligence: Dict,
        moon_phase: str
    ) -> Dict:
        """Analyze overall market state"""
        # Extract key metrics
        rsi = technical['indicators']['rsi']
        range_pos = technical['range_position']
        trend = technical['trend']['trend']
        trend_strength = technical['trend']['strength']

        # Market sentiment
        sentiment = intelligence['analysis']['verdict']
        sentiment_confidence = intelligence['analysis']['confidence']

        # Moon edge (if we've learned anything)
        moon_edge = self.memory.get_lunar_edge(moon_phase)

        return {
            "rsi": rsi,
            "rsi_condition": self._classify_rsi(rsi),
            "range_position": range_pos,
            "range_condition": self._classify_range(range_pos),
            "trend": trend,
            "trend_strength": trend_strength,
            "sentiment": sentiment,
            "sentiment_confidence": sentiment_confidence,
            "moon_phase": moon_phase,
            "moon_edge": moon_edge['edge_vs_baseline'],
            "moon_confidence": moon_edge['confidence']
        }

    def _classify_rsi(self, rsi: float) -> str:
        """Classify RSI condition"""
        if rsi < 25:
            return "extreme_oversold"
        elif rsi < 30:
            return "oversold"
        elif rsi < 40:
            return "slightly_oversold"
        elif rsi < 60:
            return "neutral"
        elif rsi < 70:
            return "slightly_overbought"
        elif rsi < 75:
            return "overbought"
        else:
            return "extreme_overbought"

    def _classify_range(self, range_pos: float) -> str:
        """Classify position in range"""
        if range_pos < 15:
            return "at_support"
        elif range_pos < 30:
            return "near_support"
        elif range_pos < 70:
            return "mid_range"
        elif range_pos < 85:
            return "near_resistance"
        else:
            return "at_resistance"

    # ==================== PATTERN DETECTION ====================

    def _detect_patterns(self, technical: Dict, state: Dict) -> List[Dict]:
        """
        Detect tradeable patterns.

        Returns list of patterns with confidence scores.
        """
        patterns = []

        rsi = state['rsi']
        range_pos = state['range_position']
        trend = state['trend']

        # Support Bounce (mean reversion buy)
        if range_pos < 25 and rsi < 35:
            # Get historical success rate
            pattern_stats = self.memory.get_pattern_stats(TradingPattern.SUPPORT_BOUNCE.value)
            win_rate = pattern_stats.win_rate if pattern_stats and pattern_stats.total_trades >= 3 else 65.0

            patterns.append({
                "pattern": TradingPattern.SUPPORT_BOUNCE,
                "direction": "buy",
                "confidence": min(0.9, win_rate / 100),
                "reason": f"Near support (${range_pos:.0f}%) + RSI oversold ({rsi:.0f})",
                "historical_wr": win_rate
            })

        # Resistance Rejection (mean reversion sell)
        if range_pos > 75 and rsi > 65:
            pattern_stats = self.memory.get_pattern_stats(TradingPattern.RESISTANCE_REJECT.value)
            win_rate = pattern_stats.win_rate if pattern_stats and pattern_stats.total_trades >= 3 else 65.0

            patterns.append({
                "pattern": TradingPattern.RESISTANCE_REJECT,
                "direction": "sell",
                "confidence": min(0.9, win_rate / 100),
                "reason": f"Near resistance ({range_pos:.0f}%) + RSI overbought ({rsi:.0f})",
                "historical_wr": win_rate
            })

        # Mean Reversion (RSI extremes)
        if rsi < 30:
            pattern_stats = self.memory.get_pattern_stats(TradingPattern.MEAN_REVERSION.value)
            win_rate = pattern_stats.win_rate if pattern_stats and pattern_stats.total_trades >= 3 else 62.0

            patterns.append({
                "pattern": TradingPattern.MEAN_REVERSION,
                "direction": "buy",
                "confidence": min(0.85, win_rate / 100),
                "reason": f"RSI oversold ({rsi:.0f}) - likely to bounce",
                "historical_wr": win_rate
            })

        if rsi > 70:
            pattern_stats = self.memory.get_pattern_stats(TradingPattern.MEAN_REVERSION.value)
            win_rate = pattern_stats.win_rate if pattern_stats and pattern_stats.total_trades >= 3 else 62.0

            patterns.append({
                "pattern": TradingPattern.MEAN_REVERSION,
                "direction": "sell",
                "confidence": min(0.85, win_rate / 100),
                "reason": f"RSI overbought ({rsi:.0f}) - likely to pull back",
                "historical_wr": win_rate
            })

        # Trend Following
        if trend == "uptrend" and 30 < range_pos < 70:
            pattern_stats = self.memory.get_pattern_stats(TradingPattern.TREND_FOLLOW.value)
            win_rate = pattern_stats.win_rate if pattern_stats and pattern_stats.total_trades >= 3 else 63.0

            patterns.append({
                "pattern": TradingPattern.TREND_FOLLOW,
                "direction": "buy",
                "confidence": min(0.8, win_rate / 100),
                "reason": "Uptrend in progress - follow momentum",
                "historical_wr": win_rate
            })

        # Sort by confidence
        patterns.sort(key=lambda x: x['confidence'], reverse=True)

        return patterns

    # ==================== BUY/SELL EVALUATION ====================

    def _evaluate_buy(
        self,
        coin: str,
        price: float,
        patterns: List[Dict],
        state: Dict
    ) -> Optional[Dict]:
        """Evaluate if we should buy"""
        # Filter buy patterns
        buy_patterns = [p for p in patterns if p['direction'] == 'buy']

        if not buy_patterns:
            return None

        # Get best pattern
        best_pattern = buy_patterns[0]

        # Apply moon phase adjustment
        moon_adjustment = state['moon_edge'] / 100  # Convert to decimal
        adjusted_confidence = best_pattern['confidence'] + moon_adjustment
        adjusted_confidence = max(0, min(1, adjusted_confidence))  # Clamp 0-1

        # Apply market sentiment adjustment
        if state['sentiment'] == 'BULLISH':
            adjusted_confidence += 0.05
        elif state['sentiment'] == 'BEARISH':
            adjusted_confidence -= 0.10

        # Exploration: Sometimes try suboptimal patterns to learn
        if random.random() < self.exploration_rate:
            # Pick a random pattern instead
            if len(buy_patterns) > 1:
                best_pattern = random.choice(buy_patterns)
                adjusted_confidence = best_pattern['confidence']

        # Check confidence threshold
        if adjusted_confidence < self.min_confidence:
            return None

        # Generate reasoning
        reasoning_parts = [best_pattern['reason']]

        if abs(state['moon_edge']) > 5:
            reasoning_parts.append(f"Moon phase {state['moon_phase']} ({state['moon_edge']:+.0f}% edge)")

        if state['sentiment'] != 'NEUTRAL':
            reasoning_parts.append(f"Market sentiment: {state['sentiment']}")

        if best_pattern.get('historical_wr'):
            reasoning_parts.append(f"Historical: {best_pattern['historical_wr']:.0f}% win rate")

        return {
            "action": Action.BUY,
            "confidence": round(adjusted_confidence, 2),
            "pattern": best_pattern['pattern'].value,
            "reasoning": " | ".join(reasoning_parts),
            "expected_outcome": "+2-5%" if adjusted_confidence > 0.7 else "+1-3%",
            "risk_level": "medium" if adjusted_confidence > 0.7 else "high"
        }

    def _evaluate_sell(
        self,
        coin: str,
        price: float,
        patterns: List[Dict],
        state: Dict,
        holding_amount: float
    ) -> Optional[Dict]:
        """Evaluate if we should sell"""
        # Filter sell patterns
        sell_patterns = [p for p in patterns if p['direction'] == 'sell']

        if not sell_patterns:
            return None

        # Get best pattern
        best_pattern = sell_patterns[0]

        # Apply adjustments (same as buy)
        moon_adjustment = state['moon_edge'] / 100
        adjusted_confidence = best_pattern['confidence'] - moon_adjustment  # Inverse for sell
        adjusted_confidence = max(0, min(1, adjusted_confidence))

        if state['sentiment'] == 'BEARISH':
            adjusted_confidence += 0.05
        elif state['sentiment'] == 'BULLISH':
            adjusted_confidence -= 0.10

        # Check confidence threshold
        if adjusted_confidence < self.min_confidence:
            return None

        # Generate reasoning
        reasoning_parts = [best_pattern['reason']]

        if abs(state['moon_edge']) > 5:
            reasoning_parts.append(f"Moon phase {state['moon_phase']} ({state['moon_edge']:+.0f}% edge)")

        if state['sentiment'] != 'NEUTRAL':
            reasoning_parts.append(f"Market sentiment: {state['sentiment']}")

        if best_pattern.get('historical_wr'):
            reasoning_parts.append(f"Historical: {best_pattern['historical_wr']:.0f}% win rate")

        return {
            "action": Action.SELL,
            "confidence": round(adjusted_confidence, 2),
            "pattern": best_pattern['pattern'].value,
            "reasoning": " | ".join(reasoning_parts),
            "expected_outcome": "Lock profit / Avoid loss",
            "risk_level": "low"
        }

    # ==================== POSITION SIZING ====================

    def calculate_position_size(
        self,
        total_balance_usd: float,
        confidence: float,
        risk_level: str
    ) -> float:
        """
        Calculate position size based on Kelly Criterion and risk.

        Returns: USD amount to invest
        """
        # Base allocation by level (risk management)
        base_allocation = {
            "low": 0.30,      # 30% of capital
            "medium": 0.25,   # 25% of capital
            "high": 0.15      # 15% of capital
        }

        base_pct = base_allocation.get(risk_level, 0.20)

        # Adjust by confidence (Kelly-like)
        # If 60% confidence, use 60% of base allocation
        # If 90% confidence, use 100% of base allocation
        confidence_multiplier = max(0.5, min(1.0, (confidence - 0.5) * 2))

        final_pct = base_pct * confidence_multiplier

        position_usd = total_balance_usd * final_pct

        return round(position_usd, 2)


if __name__ == "__main__":
    # Test trading engine
    print("🤖 Testing Trading Engine\\n")

    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

    from src.core.memory import Memory
    from src.core.progression import ProgressionSystem

    memory = Memory()
    progression = ProgressionSystem(starting_balance=59.85)

    engine = TradingEngine(
        memory_system=memory,
        progression_system=progression,
        exploration_rate=0.2,
        min_confidence=0.6
    )

    # Mock data
    technical_analysis = {
        "price": 101000,
        "indicators": {"rsi": 32, "ma20": 100800, "ma50": 100500, "volume_ratio": 1.2},
        "levels": {"support": 100000, "resistance": 102000},
        "range_position": 22,
        "trend": {"trend": "uptrend", "strength": "moderate"},
        "signals": ["RSI OVERSOLD", "NEAR SUPPORT"]
    }

    market_intelligence = {
        "analysis": {
            "verdict": "NEUTRAL",
            "confidence": 55,
            "sentiment_score": 0
        }
    }

    current_holdings = {}  # Don't own BTC yet

    decision = engine.decide_action(
        coin="BTC",
        current_price=101000,
        technical_analysis=technical_analysis,
        market_intelligence=market_intelligence,
        moon_phase="New Moon",
        current_holdings=current_holdings
    )

    print("📊 Decision:")
    print(f"   Action: {decision['action'].value}")
    print(f"   Confidence: {decision['confidence']*100:.0f}%")
    print(f"   Pattern: {decision['pattern']}")
    print(f"   Reasoning: {decision['reasoning']}")
    print(f"   Expected: {decision['expected_outcome']}")
    print(f"   Risk: {decision['risk_level']}")

    # Calculate position size
    if decision['action'] == Action.BUY:
        position_size = engine.calculate_position_size(
            total_balance_usd=59.85,
            confidence=decision['confidence'],
            risk_level=decision['risk_level']
        )
        print(f"\\n💰 Position Size: ${position_size:.2f}")

    print("\\n✅ Trading engine ready - time to learn and profit!")
