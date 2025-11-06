"""
RAYVEN - Main Trading Bot

The orchestrator that ties all systems together.

Runs the trading loop:
1. Fetch market data (price, candles, balance)
2. Analyze (technical + intelligence + moon)
3. Decide (BUY/SELL/HOLD with reasoning)
4. Execute trades
5. Learn from outcomes
6. Display on dashboard
7. Repeat

This is the "game loop" where the player learns to trade crypto.
"""

import time
import sys
from datetime import datetime
from typing import Dict, Optional

from src.api.exchange import CoinbaseAPI
from src.lunar.moon_tracker import MoonTracker
from src.analysis.technicals import TechnicalAnalysis
from src.intelligence.market_intel import MarketIntelligence
from src.core.memory import Memory, Trade
from src.core.progression import ProgressionSystem
from src.strategy.trading_engine import TradingEngine, Action
from src.interface.dashboard import Dashboard


class RAYVEN:
    """
    Main trading bot orchestrator.

    Coordinates all subsystems and runs the trading loop.
    """

    def __init__(
        self,
        starting_balance: float = 59.85,
        loop_interval_seconds: int = 60,
        dry_run: bool = False
    ):
        """
        Args:
            starting_balance: Starting balance in USD
            loop_interval_seconds: How often to check markets (default 60s)
            dry_run: If True, don't execute real trades (testing mode)
        """
        print("🤖 Initializing RAYVEN...\n")

        self.dry_run = dry_run
        self.loop_interval = loop_interval_seconds

        # Initialize all systems
        try:
            self.api = CoinbaseAPI()
            print("✅ Coinbase API connected")
        except Exception as e:
            print(f"❌ Failed to connect to Coinbase API: {e}")
            sys.exit(1)

        self.moon = MoonTracker()
        print("✅ Moon tracker initialized")

        self.memory = Memory()
        print("✅ Memory system loaded")

        # Get actual starting balance from API
        actual_balance = self.api.get_total_balance_usd()
        self.progression = ProgressionSystem(starting_balance=actual_balance)
        print(f"✅ Progression system initialized (${actual_balance:.2f})")

        self.engine = TradingEngine(
            memory_system=self.memory,
            progression_system=self.progression,
            exploration_rate=0.15,  # 15% exploration
            min_confidence=0.65      # 65% minimum confidence
        )
        print("✅ Trading engine ready")

        self.intelligence = MarketIntelligence()
        print("✅ Market intelligence ready")

        self.dashboard = Dashboard()
        print("✅ Dashboard ready")

        print("\n🚀 RAYVEN is fully operational!\n")

        if self.dry_run:
            print("⚠️  Running in DRY RUN mode - no real trades will be executed\n")

        time.sleep(2)

    # ==================== MAIN LOOP ====================

    def run(self):
        """
        Main trading loop.

        Runs forever, making decisions and executing trades.
        """
        print("🎮 Starting trading loop...\n")
        time.sleep(1)

        iteration = 0

        try:
            while True:
                iteration += 1

                # Get current progression state
                current_balance = self.api.get_total_balance_usd()

                # Update progression and check for level up
                level_up_result = self.progression.update_balance(current_balance)

                if level_up_result['leveled_up']:
                    # Show level up celebration!
                    self.dashboard.print_level_up(level_up_result)
                    time.sleep(3)

                # Get progression data
                progression_data = self.progression.get_progress()

                # Get unlocked coins
                unlocked_coins = self.progression.get_unlocked_coins()

                # For now, trade the first unlocked coin (primary focus)
                # Later can expand to trade multiple coins
                coin = unlocked_coins[0]
                pair = f"{coin}-USD"

                # Get current holdings
                holdings = self.api.get_balances()

                # Get market data
                try:
                    current_price = self.api.get_current_price(pair)
                    candles = self.api.get_ohlcv(pair, granularity="ONE_HOUR", limit=200)
                except Exception as e:
                    print(f"❌ Error fetching market data: {e}")
                    time.sleep(self.loop_interval)
                    continue

                # Technical analysis
                technical = TechnicalAnalysis.comprehensive_analysis(candles, current_price)

                # Market intelligence
                intelligence = self.intelligence.get_comprehensive_analysis(coin)

                # Moon phase
                moon_data = self.moon.get_current_phase()

                # Make decision
                decision = self.engine.decide_action(
                    coin=coin,
                    current_price=current_price,
                    technical_analysis=technical,
                    market_intelligence=intelligence,
                    moon_phase=moon_data['phase'],
                    current_holdings=holdings
                )

                # Calculate position size if buying
                position_size = None
                if decision['action'] == Action.BUY:
                    position_size = self.engine.calculate_position_size(
                        total_balance_usd=current_balance,
                        confidence=decision['confidence'],
                        risk_level=decision['risk_level']
                    )

                # Display dashboard (every iteration)
                insights = self.memory.get_insights()

                self.dashboard.display_full_status(
                    progression_data=progression_data,
                    balance_usd=current_balance,
                    coin=coin,
                    current_price=current_price,
                    technical=technical,
                    intelligence=intelligence,
                    moon_data=moon_data,
                    decision=decision,
                    position_size=position_size,
                    insights=insights
                )

                # Execute trade if action is BUY or SELL
                if decision['action'] in [Action.BUY, Action.SELL]:
                    self._execute_trade(
                        decision=decision,
                        coin=coin,
                        pair=pair,
                        current_price=current_price,
                        position_size=position_size,
                        technical=technical,
                        moon_data=moon_data
                    )

                # Log iteration
                print(f"[Iteration {iteration}] Waiting {self.loop_interval}s until next check...")
                print()

                # Sleep until next iteration
                time.sleep(self.loop_interval)

        except KeyboardInterrupt:
            print("\n\n⏸️  RAYVEN stopped by user")
            self._shutdown()

    # ==================== TRADE EXECUTION ====================

    def _execute_trade(
        self,
        decision: Dict,
        coin: str,
        pair: str,
        current_price: float,
        position_size: Optional[float],
        technical: Dict,
        moon_data: Dict
    ):
        """Execute a trade based on decision"""

        action = decision['action']

        if action == Action.BUY:
            self._execute_buy(
                coin=coin,
                pair=pair,
                current_price=current_price,
                position_size=position_size,
                decision=decision,
                technical=technical,
                moon_data=moon_data
            )

        elif action == Action.SELL:
            self._execute_sell(
                coin=coin,
                pair=pair,
                current_price=current_price,
                decision=decision,
                technical=technical,
                moon_data=moon_data
            )

    def _execute_buy(
        self,
        coin: str,
        pair: str,
        current_price: float,
        position_size: float,
        decision: Dict,
        technical: Dict,
        moon_data: Dict
    ):
        """Execute buy order"""

        if self.dry_run:
            print(f"[DRY RUN] Would BUY ${position_size:.2f} of {coin}")
            return

        try:
            # Execute market buy
            order = self.api.buy_market(pair, position_size)

            # Calculate amount received
            amount = position_size / current_price

            # Log trade
            self.dashboard.print_trade_log(
                trade_type="BUY",
                coin=coin,
                price=current_price,
                amount=amount,
                reasoning=decision['reasoning']
            )

            # Record in memory
            trade = Trade(
                timestamp=datetime.now().isoformat(),
                coin=coin,
                action="BUY",
                price=current_price,
                amount=amount,
                value_usd=position_size,
                rsi=technical['indicators']['rsi'],
                range_position=technical['range_position'],
                moon_phase=moon_data['phase'],
                sentiment_score=0,  # TODO: Add sentiment score
                pattern=decision['pattern'],
                reasoning=decision['reasoning']
            )

            self.memory.log_trade(trade)

            print(f"✅ BUY order executed: {amount:.8f} {coin} @ ${current_price:,.2f}")

        except Exception as e:
            print(f"❌ Error executing BUY: {e}")

    def _execute_sell(
        self,
        coin: str,
        pair: str,
        current_price: float,
        decision: Dict,
        technical: Dict,
        moon_data: Dict
    ):
        """Execute sell order"""

        # Get current holdings
        holdings = self.api.get_balances()
        amount = holdings.get(coin, 0)

        if amount == 0:
            print(f"⚠️  No {coin} to sell")
            return

        if self.dry_run:
            print(f"[DRY RUN] Would SELL {amount:.8f} {coin}")
            return

        try:
            # Execute market sell
            order = self.api.sell_market(pair, amount)

            # Calculate USD value
            value_usd = amount * current_price

            # Log trade
            self.dashboard.print_trade_log(
                trade_type="SELL",
                coin=coin,
                price=current_price,
                amount=amount,
                reasoning=decision['reasoning']
            )

            # Record in memory
            trade = Trade(
                timestamp=datetime.now().isoformat(),
                coin=coin,
                action="SELL",
                price=current_price,
                amount=amount,
                value_usd=value_usd,
                rsi=technical['indicators']['rsi'],
                range_position=technical['range_position'],
                moon_phase=moon_data['phase'],
                sentiment_score=0,
                pattern=decision['pattern'],
                reasoning=decision['reasoning']
            )

            self.memory.log_trade(trade)

            # Update previous BUY trade with exit data
            # Find the most recent BUY for this coin
            for t in reversed(self.memory.trades):
                if t.coin == coin and t.action == "BUY" and t.exit_price is None:
                    self.memory.update_trade_outcome(
                        entry_timestamp=t.timestamp,
                        exit_price=current_price,
                        exit_timestamp=datetime.now().isoformat()
                    )
                    break

            print(f"✅ SELL order executed: {amount:.8f} {coin} @ ${current_price:,.2f}")

        except Exception as e:
            print(f"❌ Error executing SELL: {e}")

    # ==================== SHUTDOWN ====================

    def _shutdown(self):
        """Clean shutdown"""
        print("\n📊 Final Statistics:\n")

        # Get final stats
        final_balance = self.api.get_total_balance_usd()
        progress = self.progression.get_progress()
        insights = self.memory.get_insights()

        print(f"Final Balance: ${final_balance:.2f}")
        print(f"Total P/L: ${progress['profit_loss']:+.2f} ({progress['profit_loss_pct']:+.1f}%)")
        print(f"Current Level: {progress['current_level']} - {progress['level_name']}")

        if "total_trades" in insights:
            print(f"\nTotal Trades: {insights['total_trades']}")
            print(f"Win Rate: {insights['win_rate']:.1f}%")
            print(f"Total Profit: {insights['total_profit_pct']:+.2f}%")

        print("\n👋 Thanks for playing RAYVEN!")
        print("💾 All progress has been saved.")
        print()


if __name__ == "__main__":
    # Parse command line args
    dry_run = "--dry-run" in sys.argv

    # Create and run RAYVEN
    rayven = RAYVEN(
        starting_balance=59.85,
        loop_interval_seconds=60,  # Check every minute
        dry_run=dry_run
    )

    rayven.run()
