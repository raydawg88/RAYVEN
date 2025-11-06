"""
RAYVEN Dashboard

Live trading dashboard with explanatory logs.

Shows:
- Current level & progress
- Market analysis (technical + intelligence + moon)
- Trading decisions with reasoning
- Learning insights
- Trade history
"""

from typing import Dict, List, Optional
from datetime import datetime
import os


class Dashboard:
    """
    Terminal dashboard for RAYVEN trading system.

    Displays all system state and reasoning in human-readable format.
    """

    def __init__(self):
        self.width = 80
        self.logs: List[str] = []

    # ==================== DISPLAY COMPONENTS ====================

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_header(self):
        """Print RAYVEN header"""
        print("=" * self.width)
        print("🤖 RAYVEN - Reinforcement Learning Crypto Trader".center(self.width))
        print("=" * self.width)
        print()

    def print_status(self, progression_data: Dict, balance_usd: float):
        """
        Print current status (level, balance, progress).

        Args:
            progression_data: Output from progression.get_progress()
            balance_usd: Current total balance in USD
        """
        print("📊 STATUS")
        print("-" * self.width)

        level = progression_data['current_level']
        level_name = progression_data['level_name']
        progress_pct = progression_data['progress_to_next']
        next_milestone = progression_data['next_milestone']
        profit_loss = progression_data['profit_loss']
        profit_loss_pct = progression_data['profit_loss_pct']

        print(f"Level: {level} - {level_name}")
        print(f"Balance: ${balance_usd:.2f} | P/L: ${profit_loss:+.2f} ({profit_loss_pct:+.1f}%)")

        if next_milestone:
            needed = progression_data['amount_needed']
            print(f"Progress: {self._progress_bar(progress_pct)} {progress_pct:.1f}%")
            print(f"Next Level: ${next_milestone:.2f} (${needed:.2f} to go)")

            if progression_data['next_unlock']:
                print(f"Next Unlock: {', '.join(progression_data['next_unlock'])}")
        else:
            print("🎉 MAX LEVEL REACHED!")

        print(f"Unlocked Coins: {', '.join(progression_data['unlocked_coins'])}")
        print()

    def print_market_analysis(
        self,
        coin: str,
        current_price: float,
        technical: Dict,
        intelligence: Dict,
        moon_data: Dict
    ):
        """
        Print market analysis.

        Args:
            coin: Coin symbol (e.g., "BTC")
            current_price: Current price in USD
            technical: Technical analysis output
            intelligence: Market intelligence output
            moon_data: Moon phase data
        """
        print(f"🔍 MARKET ANALYSIS - {coin}")
        print("-" * self.width)

        print(f"Price: ${current_price:,.2f}")
        print()

        # Technical indicators
        print("📊 Technical Indicators:")
        indicators = technical['indicators']
        print(f"   RSI: {indicators['rsi']:.1f} {self._rsi_emoji(indicators['rsi'])}")
        print(f"   MA20: ${indicators['ma20']:,.2f}")
        print(f"   Volume: {indicators['volume_ratio']:.2f}x average")

        # Support/Resistance
        levels = technical['levels']
        range_pos = technical['range_position']
        print(f"\n🎯 Levels:")
        print(f"   Support: ${levels['support']:,.2f}")
        print(f"   Current: ${current_price:,.2f} ({range_pos:.0f}% in range)")
        print(f"   Resistance: ${levels['resistance']:,.2f}")

        # Trend
        trend = technical['trend']
        print(f"\n📈 Trend: {trend['trend'].upper()} ({trend['strength']})")

        # Market Intelligence
        analysis = intelligence['analysis']
        print(f"\n🌐 Market Sentiment: {analysis['verdict']} ({analysis['confidence']}% confidence)")

        # Moon Phase
        print(f"\n🌙 Moon Phase: {moon_data['phase']} ({moon_data['illumination']:.0f}% illuminated)")
        print(f"   Trading Bias: {moon_data['trading_bias']}")

        # Signals
        if technical['signals']:
            print(f"\n⚡ Signals:")
            for signal in technical['signals'][:3]:  # Top 3 signals
                print(f"   • {signal}")

        print()

    def print_decision(self, decision: Dict, position_size: Optional[float] = None):
        """
        Print trading decision with reasoning.

        Args:
            decision: Decision output from trading engine
            position_size: Position size in USD (if BUY)
        """
        action = decision['action'].value
        confidence = decision['confidence']
        pattern = decision['pattern']
        reasoning = decision['reasoning']
        expected = decision['expected_outcome']
        risk = decision['risk_level']

        # Action emoji
        action_emoji = {
            "BUY": "💰",
            "SELL": "💸",
            "HOLD": "⏸️"
        }

        print(f"🎯 DECISION")
        print("-" * self.width)
        print(f"Action: {action_emoji.get(action, '')} {action}")
        print(f"Confidence: {confidence*100:.0f}% {'🔥' if confidence > 0.75 else '⚠️' if confidence < 0.65 else '✓'}")

        if pattern:
            print(f"Pattern: {pattern.replace('_', ' ').title()}")

        print(f"Risk Level: {risk.upper()}")
        print()

        print("💭 Reasoning:")
        # Split reasoning by | and display each part on new line
        for part in reasoning.split(" | "):
            print(f"   • {part}")

        print()
        print(f"📈 Expected Outcome: {expected}")

        if position_size:
            print(f"💵 Position Size: ${position_size:.2f}")

        print()

    def print_learning_insights(self, insights: Dict):
        """
        Print what RAYVEN has learned.

        Args:
            insights: Output from memory.get_insights()
        """
        if "message" in insights:
            print("📚 LEARNING")
            print("-" * self.width)
            print(f"   {insights['message']}")
            print()
            return

        print("📚 LEARNING INSIGHTS")
        print("-" * self.width)

        print(f"Total Trades: {insights['total_trades']}")
        print(f"Win Rate: {insights['win_rate']:.1f}%")
        print(f"Total Profit: {insights['total_profit_pct']:+.2f}%")
        print()

        if insights['best_patterns']:
            print("✅ Best Patterns:")
            for pattern in insights['best_patterns']:
                print(f"   • {pattern.replace('_', ' ').title()}")
            print()

        if insights['avoid_patterns']:
            print("❌ Avoid Patterns:")
            for pattern in insights['avoid_patterns']:
                print(f"   • {pattern.replace('_', ' ').title()}")
            print()

        if insights['lunar_correlations']:
            print("🌙 Moon Phase Insights:")
            for correlation in insights['lunar_correlations']:
                print(f"   • {correlation}")
            print()

        print("📖 Lessons Learned:")
        for lesson in insights['lessons_learned']:
            print(f"   {lesson}")
        print()

    def print_trade_log(self, trade_type: str, coin: str, price: float, amount: float, reasoning: str):
        """
        Log a trade execution.

        Args:
            trade_type: "BUY" or "SELL"
            coin: Coin symbol
            price: Execution price
            amount: Amount traded
            reasoning: Why the trade was made
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        emoji = "💰" if trade_type == "BUY" else "💸"

        log_entry = f"[{timestamp}] {emoji} {trade_type} {amount:.8f} {coin} @ ${price:,.2f}"
        print(log_entry)
        print(f"           Reason: {reasoning}")
        print()

        self.logs.append(log_entry)

    def print_level_up(self, result: Dict):
        """
        Print level-up celebration.

        Args:
            result: Level-up result from progression.update_balance()
        """
        if not result['leveled_up']:
            return

        print()
        print("=" * self.width)
        print("🎉 LEVEL UP! 🎉".center(self.width))
        print("=" * self.width)
        print()
        print(f"   {result['achievement']}")
        print(f"   {result['description']}")
        print()

        if result['unlocked_coins']:
            print(f"   🔓 Unlocked: {', '.join(result['unlocked_coins'])}")
            print()

        print("=" * self.width)
        print()

    def print_separator(self):
        """Print section separator"""
        print()
        print("~" * self.width)
        print()

    # ==================== HELPER METHODS ====================

    def _progress_bar(self, percentage: float, width: int = 20) -> str:
        """Generate ASCII progress bar"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"

    def _rsi_emoji(self, rsi: float) -> str:
        """Get emoji for RSI value"""
        if rsi < 30:
            return "🔴 OVERSOLD"
        elif rsi > 70:
            return "🟢 OVERBOUGHT"
        else:
            return "⚪ NEUTRAL"

    # ==================== COMBINED DISPLAYS ====================

    def display_full_status(
        self,
        progression_data: Dict,
        balance_usd: float,
        coin: str,
        current_price: float,
        technical: Dict,
        intelligence: Dict,
        moon_data: Dict,
        decision: Dict,
        position_size: Optional[float],
        insights: Dict
    ):
        """
        Display complete dashboard (all sections).

        Use this for periodic full updates.
        """
        self.clear_screen()
        self.print_header()
        self.print_status(progression_data, balance_usd)
        self.print_market_analysis(coin, current_price, technical, intelligence, moon_data)
        self.print_decision(decision, position_size)
        self.print_learning_insights(insights)

    def display_quick_update(
        self,
        coin: str,
        current_price: float,
        decision: Dict,
        position_size: Optional[float]
    ):
        """
        Display quick update (just decision, no full refresh).

        Use this for rapid polling updates.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        action = decision['action'].value
        confidence = decision['confidence']

        print(f"[{timestamp}] {coin} ${current_price:,.2f} | {action} ({confidence*100:.0f}% conf)")


if __name__ == "__main__":
    # Test dashboard
    print("🖥️  Testing Dashboard Display\n")

    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

    dashboard = Dashboard()

    # Mock data
    progression_data = {
        'current_level': 1,
        'level_name': '🥉 Bitcoin Apprentice',
        'current_balance': 59.85,
        'profit_loss': 0.0,
        'profit_loss_pct': 0.0,
        'progress_to_next': 0.0,
        'next_milestone': 85.0,
        'amount_needed': 25.15,
        'unlocked_coins': ['BTC'],
        'next_unlock': ['ETH']
    }

    technical = {
        'price': 101234.56,
        'indicators': {'rsi': 32.5, 'ma20': 100800, 'ma50': 100500, 'volume_ratio': 1.3},
        'levels': {'support': 100000, 'resistance': 102500},
        'range_position': 24,
        'trend': {'trend': 'uptrend', 'strength': 'moderate'},
        'signals': ['RSI OVERSOLD - Potential buy', 'NEAR SUPPORT - Bounce opportunity']
    }

    intelligence = {
        'analysis': {
            'verdict': 'NEUTRAL',
            'confidence': 55,
            'sentiment_score': 0
        }
    }

    moon_data = {
        'phase': 'First Quarter',
        'illumination': 52.3,
        'trading_bias': 'Slightly bullish - building energy toward full moon'
    }

    from src.strategy.trading_engine import Action

    decision = {
        'action': Action.BUY,
        'confidence': 0.68,
        'pattern': 'support_bounce',
        'reasoning': 'Near support (24%) + RSI oversold (32) | Historical: 65% win rate',
        'expected_outcome': '+2-5%',
        'risk_level': 'medium'
    }

    insights = {
        'total_trades': 5,
        'win_rate': 60.0,
        'total_profit_pct': 3.5,
        'best_patterns': ['support_bounce'],
        'avoid_patterns': [],
        'lunar_correlations': [],
        'lessons_learned': ['📚 Keep trading to learn patterns']
    }

    # Display full dashboard
    dashboard.display_full_status(
        progression_data=progression_data,
        balance_usd=59.85,
        coin="BTC",
        current_price=101234.56,
        technical=technical,
        intelligence=intelligence,
        moon_data=moon_data,
        decision=decision,
        position_size=14.96,
        insights=insights
    )

    # Test level up
    level_up_result = {
        'leveled_up': True,
        'new_level': 2,
        'achievement': '🥈 Dual Asset Trader',
        'description': 'Add Ethereum - the smart contract king',
        'unlocked_coins': ['ETH']
    }
    dashboard.print_level_up(level_up_result)

    # Test trade log
    dashboard.print_trade_log(
        trade_type="BUY",
        coin="BTC",
        price=101234.56,
        amount=0.000148,
        reasoning="Support bounce pattern - RSI oversold"
    )

    print("✅ Dashboard ready for live trading!")
