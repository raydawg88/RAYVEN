"""
RAYVEN - Main Trading Bot (Web Interface Version)

Runs the trading loop and broadcasts to web interface via WebSocket.
"""

import time
import sys
import threading
from datetime import datetime
from typing import Dict, Optional

from src.api.exchange import CoinbaseAPI
from src.lunar.moon_tracker import MoonTracker
from src.analysis.technicals import TechnicalAnalysis
from src.intelligence.market_intel import MarketIntelligence
from src.core.memory import Memory, Trade
from src.core.progression import ProgressionSystem
from src.strategy.trading_engine import TradingEngine, Action

# Import web interface
sys.path.insert(0, 'web')
from web.app import socketio, update_state, emit_step, emit_trade, emit_level_up, emit_status, run_server


class RAYVEN:
    """
    Main trading bot orchestrator with web interface.
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
            emit_status("Coinbase API connected")
        except Exception as e:
            print(f"❌ Failed to connect to Coinbase API: {e}")
            emit_status(f"ERROR: Coinbase API failed - {e}")
            sys.exit(1)

        self.moon = MoonTracker()
        print("✅ Moon tracker initialized")
        emit_status("Moon tracker initialized")

        self.memory = Memory()
        print("✅ Memory system loaded")
        emit_status("Memory system loaded")

        # Get actual starting balance from API
        actual_balance = self.api.get_total_balance_usd()
        self.progression = ProgressionSystem(starting_balance=actual_balance)
        print(f"✅ Progression system initialized (${actual_balance:.2f})")
        emit_status(f"Progression system initialized - ${actual_balance:.2f}")

        self.engine = TradingEngine(
            memory_system=self.memory,
            progression_system=self.progression,
            exploration_rate=0.15,
            min_confidence=0.65
        )
        print("✅ Trading engine ready")
        emit_status("Trading engine ready")

        self.intelligence = MarketIntelligence()
        print("✅ Market intelligence ready")
        emit_status("Market intelligence ready")

        print("\n🚀 RAYVEN is fully operational!")
        print("🌐 Open http://localhost:5001 in your browser\n")

        if self.dry_run:
            print("⚠️  Running in DRY RUN mode - no real trades will be executed\n")
            emit_status("⚠️ DRY RUN MODE - No real trades")

        emit_status("🚀 RAYVEN is fully operational!")

        time.sleep(2)

    # ==================== MAIN LOOP ====================

    def run(self):
        """
        Main trading loop with web interface updates.
        """
        print("🎮 Starting trading loop...\n")
        emit_status("Starting trading loop...")
        time.sleep(1)

        iteration = 0

        try:
            while True:
                iteration += 1
                emit_status(f"📊 Starting iteration {iteration}...")

                # Step 1: Fetch balance
                emit_step(0, "Fetching balance...")
                time.sleep(0.5)
                current_balance = self.api.get_total_balance_usd()

                # Step 2: Check progression & level up
                emit_step(1, "Checking progression...")
                time.sleep(0.5)
                level_up_result = self.progression.update_balance(current_balance)

                if level_up_result['leveled_up']:
                    print(f"\n🎉 LEVEL UP! Level {level_up_result['new_level']}")
                    emit_level_up(level_up_result)
                    time.sleep(3)

                progression_data = self.progression.get_progress()
                unlocked_coins = self.progression.get_unlocked_coins()
                coin = unlocked_coins[0]
                pair = f"{coin}-USD"

                # Update state
                update_state({
                    "level": progression_data['current_level'],
                    "balance": current_balance,
                    "progress": progression_data['progress_to_next'],
                    "target": progression_data['next_milestone'] or 0,
                    "coin": coin
                })

                # Step 3: Fetch market data
                emit_step(2, f"Fetching {coin} price...")
                time.sleep(0.5)
                try:
                    current_price = self.api.get_current_price(pair)
                    candles = self.api.get_ohlcv(pair, granularity="ONE_HOUR", limit=200)
                except Exception as e:
                    print(f"❌ Error fetching market data: {e}")
                    emit_status(f"Error: {e}")
                    time.sleep(self.loop_interval)
                    continue

                # Step 4: Technical analysis
                emit_step(3, "Running technical analysis...")
                time.sleep(0.5)
                technical = TechnicalAnalysis.comprehensive_analysis(candles, current_price)

                # Step 5: Market intelligence
                emit_step(4, "Gathering market intelligence...")
                time.sleep(0.5)
                intelligence = self.intelligence.get_comprehensive_analysis(coin)

                # Step 6: Moon phase
                emit_step(5, "Checking moon phase...")
                time.sleep(0.5)
                moon_data = self.moon.get_current_phase()

                # Step 7: Make decision
                emit_step(6, "Making trading decision...")
                time.sleep(0.5)
                holdings = self.api.get_balances()

                decision = self.engine.decide_action(
                    coin=coin,
                    current_price=current_price,
                    technical_analysis=technical,
                    market_intelligence=intelligence,
                    moon_phase=moon_data['phase'],
                    current_holdings=holdings
                )

                position_size = None
                if decision['action'] == Action.BUY:
                    position_size = self.engine.calculate_position_size(
                        total_balance_usd=current_balance,
                        confidence=decision['confidence'],
                        risk_level=decision['risk_level']
                    )

                # Emit decision
                action_str = decision['action'].value
                emit_status(f"Decision: {action_str} {coin} - {decision['confidence']*100:.0f}% confidence")

                # Step 8: Execute trade
                emit_step(7, "Executing trade...")
                time.sleep(0.5)

                trade_outcome = None
                if decision['action'] in [Action.BUY, Action.SELL]:
                    trade_outcome = self._execute_trade(
                        decision=decision,
                        coin=coin,
                        pair=pair,
                        current_price=current_price,
                        position_size=position_size,
                        technical=technical,
                        moon_data=moon_data
                    )
                else:
                    emit_status("No trade - HOLDING")

                # Step 9: Update learning
                emit_step(8, "Updating memory...")
                time.sleep(0.5)

                # Send trade to web if executed
                if trade_outcome:
                    emit_trade(trade_outcome)

                # Complete cycle
                emit_status(f"✅ Iteration {iteration} complete - waiting {self.loop_interval}s...")
                time.sleep(self.loop_interval)

        except KeyboardInterrupt:
            print("\n\n⏸️  RAYVEN stopped by user")
            emit_status("⏸️ RAYVEN stopped by user")
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
    ) -> Optional[Dict]:
        """Execute a trade and return outcome for web display"""

        action = decision['action']

        if action == Action.BUY:
            return self._execute_buy(
                coin, pair, current_price, position_size,
                decision, technical, moon_data
            )
        elif action == Action.SELL:
            return self._execute_sell(
                coin, pair, current_price,
                decision, technical, moon_data
            )

        return None

    def _execute_buy(
        self,
        coin: str,
        pair: str,
        current_price: float,
        position_size: float,
        decision: Dict,
        technical: Dict,
        moon_data: Dict
    ) -> Dict:
        """Execute buy order"""

        if self.dry_run:
            emit_status(f"[DRY RUN] Would BUY ${position_size:.2f} of {coin}")
            return {
                "outcome": "hold",
                "pattern": decision['pattern'],
                "profit": "DRY RUN"
            }

        try:
            # Execute market buy
            order = self.api.buy_market(pair, position_size)
            amount = position_size / current_price

            # Log trade
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
                sentiment_score=0,
                pattern=decision['pattern'],
                reasoning=decision['reasoning']
            )

            self.memory.log_trade(trade)
            emit_status(f"✅ BUY executed: {amount:.8f} {coin} @ ${current_price:,.2f}")

            return {
                "outcome": "hold",  # Won't know if win/loss until we sell
                "pattern": decision['pattern'],
                "profit": f"${position_size:.2f}"
            }

        except Exception as e:
            emit_status(f"❌ Error executing BUY: {e}")
            return None

    def _execute_sell(
        self,
        coin: str,
        pair: str,
        current_price: float,
        decision: Dict,
        technical: Dict,
        moon_data: Dict
    ) -> Dict:
        """Execute sell order"""

        holdings = self.api.get_balances()
        amount = holdings.get(coin, 0)

        if amount == 0:
            emit_status(f"⚠️ No {coin} to sell")
            return None

        if self.dry_run:
            emit_status(f"[DRY RUN] Would SELL {amount:.8f} {coin}")
            return {
                "outcome": "win",
                "pattern": decision['pattern'],
                "profit": "+2.5%"
            }

        try:
            # Execute market sell
            order = self.api.sell_market(pair, amount)
            value_usd = amount * current_price

            # Log trade
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

            # Update previous BUY with exit data
            for t in reversed(self.memory.trades):
                if t.coin == coin and t.action == "BUY" and t.exit_price is None:
                    self.memory.update_trade_outcome(
                        entry_timestamp=t.timestamp,
                        exit_price=current_price,
                        exit_timestamp=datetime.now().isoformat()
                    )

                    # Determine outcome
                    outcome = "win" if t.profit_loss > 0 else "loss"
                    profit = f"{t.profit_loss_pct:+.2f}%"

                    emit_status(f"✅ SELL executed: {amount:.8f} {coin} @ ${current_price:,.2f} | {profit}")

                    return {
                        "outcome": outcome,
                        "pattern": decision['pattern'],
                        "profit": profit
                    }
                    break

            return {
                "outcome": "hold",
                "pattern": decision['pattern'],
                "profit": "N/A"
            }

        except Exception as e:
            emit_status(f"❌ Error executing SELL: {e}")
            return None

    # ==================== SHUTDOWN ====================

    def _shutdown(self):
        """Clean shutdown"""
        print("\n📊 Final Statistics:\n")

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

    # Start web server in separate thread
    web_thread = threading.Thread(target=run_server, daemon=True)
    web_thread.start()

    print("⏳ Waiting for web server to start...")
    time.sleep(3)

    # Create and run RAYVEN
    rayven = RAYVEN(
        starting_balance=59.85,
        loop_interval_seconds=60,
        dry_run=dry_run
    )

    rayven.run()
