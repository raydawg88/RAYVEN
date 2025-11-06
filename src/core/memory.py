"""
Learning & Memory System

The brain of RAYVEN - tracks what works and what doesn't.

Stores:
- Trade history with outcomes
- Pattern win rates
- Moon phase correlations
- Best entry/exit times
- What the player has learned
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class Trade:
    """Single trade record"""
    timestamp: str
    coin: str
    action: str  # BUY, SELL
    price: float
    amount: float
    value_usd: float

    # Context at time of trade
    rsi: float
    range_position: float
    moon_phase: str
    sentiment_score: int

    # Pattern/strategy used
    pattern: str  # e.g., "support_bounce", "breakout", "mean_reversion"
    reasoning: str

    # Outcome (filled after exit)
    exit_price: Optional[float] = None
    exit_timestamp: Optional[str] = None
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None
    win: Optional[bool] = None


@dataclass
class PatternStats:
    """Statistics for a trading pattern"""
    pattern_name: str
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    avg_profit: float
    avg_loss: float
    best_trade: float
    worst_trade: float
    total_profit: float


class Memory:
    """
    Learning and memory system.

    Persists all trades and learns from outcomes.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self.trades_file = os.path.join(data_dir, "trades.json")
        self.patterns_file = os.path.join(data_dir, "patterns.json")
        self.lunar_file = os.path.join(data_dir, "lunar_correlations.json")

        self.trades: List[Trade] = self._load_trades()
        self.patterns: Dict[str, PatternStats] = self._load_patterns()
        self.lunar_data: Dict = self._load_lunar_data()

    # ==================== TRADE LOGGING ====================

    def log_trade(self, trade: Trade):
        """Record a new trade"""
        self.trades.append(trade)
        self._save_trades()

    def update_trade_outcome(self, entry_timestamp: str, exit_price: float, exit_timestamp: str):
        """Update trade with exit data"""
        for trade in self.trades:
            if trade.timestamp == entry_timestamp and trade.action == "BUY":
                trade.exit_price = exit_price
                trade.exit_timestamp = exit_timestamp
                trade.profit_loss = (exit_price - trade.price) * trade.amount
                trade.profit_loss_pct = ((exit_price - trade.price) / trade.price) * 100 if trade.price > 0 else 0
                trade.win = trade.profit_loss > 0

                # Update pattern stats
                self._update_pattern_stats(trade)

                # Update lunar correlations
                self._update_lunar_correlations(trade)

                self._save_trades()
                break

    # ==================== PATTERN LEARNING ====================

    def _update_pattern_stats(self, trade: Trade):
        """Update statistics for this pattern"""
        pattern = trade.pattern

        if pattern not in self.patterns:
            self.patterns[pattern] = PatternStats(
                pattern_name=pattern,
                total_trades=0,
                wins=0,
                losses=0,
                win_rate=0.0,
                avg_profit=0.0,
                avg_loss=0.0,
                best_trade=0.0,
                worst_trade=0.0,
                total_profit=0.0
            )

        stats = self.patterns[pattern]
        stats.total_trades += 1

        if trade.win:
            stats.wins += 1
            stats.avg_profit = ((stats.avg_profit * (stats.wins - 1)) + trade.profit_loss_pct) / stats.wins
            if trade.profit_loss_pct > stats.best_trade:
                stats.best_trade = trade.profit_loss_pct
        else:
            stats.losses += 1
            stats.avg_loss = ((stats.avg_loss * (stats.losses - 1)) + trade.profit_loss_pct) / stats.losses
            if trade.profit_loss_pct < stats.worst_trade:
                stats.worst_trade = trade.profit_loss_pct

        stats.win_rate = (stats.wins / stats.total_trades) * 100 if stats.total_trades > 0 else 0
        stats.total_profit += trade.profit_loss_pct

        self._save_patterns()

    def get_pattern_stats(self, pattern: str) -> Optional[PatternStats]:
        """Get statistics for a pattern"""
        return self.patterns.get(pattern)

    def get_all_patterns(self) -> List[PatternStats]:
        """Get all pattern statistics, sorted by win rate"""
        return sorted(self.patterns.values(), key=lambda x: x.win_rate, reverse=True)

    def get_best_patterns(self, min_trades: int = 5) -> List[PatternStats]:
        """Get patterns with good win rates (min trades for confidence)"""
        return [
            p for p in self.get_all_patterns()
            if p.total_trades >= min_trades and p.win_rate >= 60
        ]

    # ==================== LUNAR CORRELATION ====================

    def _update_lunar_correlations(self, trade: Trade):
        """Track moon phase correlations"""
        phase = trade.moon_phase

        if phase not in self.lunar_data:
            self.lunar_data[phase] = {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "avg_profit_pct": 0.0
            }

        data = self.lunar_data[phase]
        data["total_trades"] += 1

        if trade.win:
            data["wins"] += 1
        else:
            data["losses"] += 1

        data["win_rate"] = (data["wins"] / data["total_trades"]) * 100 if data["total_trades"] > 0 else 0

        # Update average profit
        total_profit = data.get("total_profit", 0) + trade.profit_loss_pct
        data["total_profit"] = total_profit
        data["avg_profit_pct"] = total_profit / data["total_trades"]

        self._save_lunar_data()

    def get_lunar_edge(self, moon_phase: str) -> Dict:
        """
        Get the statistical edge for a moon phase.

        Returns:
            {"win_rate": 68.2, "edge_vs_baseline": +8.2, "confidence": "high"}
        """
        if moon_phase not in self.lunar_data:
            return {"win_rate": 50.0, "edge_vs_baseline": 0.0, "confidence": "none", "sample_size": 0}

        data = self.lunar_data[moon_phase]

        # Calculate baseline (all phases)
        total_trades = sum(d["total_trades"] for d in self.lunar_data.values())
        total_wins = sum(d["wins"] for d in self.lunar_data.values())
        baseline_wr = (total_wins / total_trades * 100) if total_trades > 0 else 50.0

        edge = data["win_rate"] - baseline_wr

        # Confidence based on sample size
        if data["total_trades"] < 10:
            confidence = "low"
        elif data["total_trades"] < 30:
            confidence = "medium"
        else:
            confidence = "high"

        return {
            "win_rate": data["win_rate"],
            "edge_vs_baseline": round(edge, 2),
            "confidence": confidence,
            "sample_size": data["total_trades"]
        }

    # ==================== INSIGHTS ====================

    def get_insights(self) -> Dict:
        """
        Get learning insights - what has the player learned?

        Returns key learnings from trade history.
        """
        if not self.trades:
            return {"message": "No trades yet - still learning!"}

        completed_trades = [t for t in self.trades if t.win is not None]

        if not completed_trades:
            return {"message": "Trades in progress - outcomes pending"}

        wins = sum(1 for t in completed_trades if t.win)
        total = len(completed_trades)
        win_rate = (wins / total) * 100 if total > 0 else 0

        total_profit = sum(t.profit_loss_pct for t in completed_trades)

        best_patterns = self.get_best_patterns(min_trades=3)
        worst_patterns = [p for p in self.get_all_patterns() if p.total_trades >= 3 and p.win_rate < 40]

        # Lunar insights
        lunar_insights = []
        for phase in self.lunar_data:
            edge = self.get_lunar_edge(phase)
            if edge["sample_size"] >= 5 and abs(edge["edge_vs_baseline"]) > 5:
                lunar_insights.append(f"{phase}: {edge['edge_vs_baseline']:+.1f}% edge")

        return {
            "total_trades": total,
            "win_rate": round(win_rate, 2),
            "total_profit_pct": round(total_profit, 2),
            "best_patterns": [p.pattern_name for p in best_patterns[:3]],
            "avoid_patterns": [p.pattern_name for p in worst_patterns[:3]],
            "lunar_correlations": lunar_insights,
            "lessons_learned": self._generate_lessons()
        }

    def _generate_lessons(self) -> List[str]:
        """Generate human-readable lessons learned"""
        lessons = []

        # Pattern lessons
        best = self.get_best_patterns(min_trades=5)
        if best:
            top = best[0]
            lessons.append(f"✅ {top.pattern_name} works well ({top.win_rate:.1f}% win rate)")

        worst = [p for p in self.get_all_patterns() if p.total_trades >= 5 and p.win_rate < 40]
        if worst:
            bad = worst[0]
            lessons.append(f"❌ Avoid {bad.pattern_name} ({bad.win_rate:.1f}% win rate)")

        # Lunar lessons
        for phase, data in self.lunar_data.items():
            if data["total_trades"] >= 10:
                edge = self.get_lunar_edge(phase)
                if edge["edge_vs_baseline"] > 10:
                    lessons.append(f"🌙 {phase} shows {edge['edge_vs_baseline']:+.1f}% edge")

        if not lessons:
            lessons.append("📚 Keep trading to learn patterns")

        return lessons

    # ==================== PERSISTENCE ====================

    def _load_trades(self) -> List[Trade]:
        """Load trades from disk"""
        if not os.path.exists(self.trades_file):
            return []

        with open(self.trades_file, 'r') as f:
            data = json.load(f)
            return [Trade(**t) for t in data]

    def _save_trades(self):
        """Save trades to disk"""
        with open(self.trades_file, 'w') as f:
            json.dump([asdict(t) for t in self.trades], f, indent=2)

    def _load_patterns(self) -> Dict[str, PatternStats]:
        """Load pattern stats from disk"""
        if not os.path.exists(self.patterns_file):
            return {}

        with open(self.patterns_file, 'r') as f:
            data = json.load(f)
            return {name: PatternStats(**stats) for name, stats in data.items()}

    def _save_patterns(self):
        """Save pattern stats to disk"""
        with open(self.patterns_file, 'w') as f:
            json.dump({name: asdict(stats) for name, stats in self.patterns.items()}, f, indent=2)

    def _load_lunar_data(self) -> Dict:
        """Load lunar correlations from disk"""
        if not os.path.exists(self.lunar_file):
            return {}

        with open(self.lunar_file, 'r') as f:
            return json.load(f)

    def _save_lunar_data(self):
        """Save lunar correlations to disk"""
        with open(self.lunar_file, 'w') as f:
            json.dump(self.lunar_data, f, indent=2)


if __name__ == "__main__":
    # Test memory system
    print("🧠 Testing Learning & Memory System\n")

    memory = Memory()

    # Simulate a trade
    trade = Trade(
        timestamp=datetime.now().isoformat(),
        coin="BTC",
        action="BUY",
        price=101000,
        amount=0.0001,
        value_usd=10.1,
        rsi=35,
        range_position=15,
        moon_phase="New Moon",
        sentiment_score=10,
        pattern="support_bounce",
        reasoning="RSI oversold + near support + bullish moon phase"
    )

    print("📝 Logging trade:")
    print(f"   {trade.action} {trade.coin} @ ${trade.price:,.2f}")
    print(f"   Pattern: {trade.pattern}")
    print(f"   Moon: {trade.moon_phase}")

    memory.log_trade(trade)

    # Simulate exit
    print("\n✅ Simulating profitable exit...")
    memory.update_trade_outcome(
        entry_timestamp=trade.timestamp,
        exit_price=102500,
        exit_timestamp=datetime.now().isoformat()
    )

    # Get insights
    print("\n🎓 Learning Insights:")
    insights = memory.get_insights()
    print(f"   Total Trades: {insights['total_trades']}")
    print(f"   Win Rate: {insights['win_rate']}%")
    print(f"   Total Profit: {insights['total_profit_pct']:+.2f}%")

    print("\n📚 Lessons Learned:")
    for lesson in insights['lessons_learned']:
        print(f"   {lesson}")

    # Pattern stats
    pattern_stats = memory.get_pattern_stats("support_bounce")
    if pattern_stats:
        print(f"\n📊 Pattern: {pattern_stats.pattern_name}")
        print(f"   Trades: {pattern_stats.total_trades}")
        print(f"   Win Rate: {pattern_stats.win_rate:.1f}%")
        print(f"   Avg Profit: {pattern_stats.avg_profit:.2f}%")

    print("\n✅ Learning system ready - player can now learn from experience!")
