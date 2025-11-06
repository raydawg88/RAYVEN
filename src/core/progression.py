"""
Progression & Level System

The "game" mechanics of RAYVEN.

Tracks:
- Current level (1-6+)
- Balance milestones ($85, $120, $180, $270, etc.)
- Unlocked coins at each level
- Progress toward next level
- Achievements and level-ups

Each level unlocks a new coin to trade.
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Level:
    """Level definition"""
    level_number: int
    milestone_usd: float
    unlocked_coins: List[str]
    description: str
    achievement_name: str


class ProgressionSystem:
    """
    Game progression mechanics.

    Tracks current level and unlocks new trading pairs at milestones.
    """

    # Level definitions - the game roadmap
    LEVELS = [
        Level(
            level_number=1,
            milestone_usd=85.0,
            unlocked_coins=["BTC"],
            description="Master Bitcoin - the foundation",
            achievement_name="🥉 Bitcoin Apprentice"
        ),
        Level(
            level_number=2,
            milestone_usd=120.0,
            unlocked_coins=["BTC", "ETH"],
            description="Add Ethereum - the smart contract king",
            achievement_name="🥈 Dual Asset Trader"
        ),
        Level(
            level_number=3,
            milestone_usd=180.0,
            unlocked_coins=["BTC", "ETH", "SOL"],
            description="Add Solana - the speed demon",
            achievement_name="🥇 Triple Threat"
        ),
        Level(
            level_number=4,
            milestone_usd=270.0,
            unlocked_coins=["BTC", "ETH", "SOL", "XRP", "AVAX"],
            description="Expand to XRP & AVAX",
            achievement_name="💎 Multi-Asset Master"
        ),
        Level(
            level_number=5,
            milestone_usd=400.0,
            unlocked_coins=["BTC", "ETH", "SOL", "XRP", "AVAX", "LINK", "DOT", "MATIC"],
            description="Expand portfolio to 8 coins",
            achievement_name="⭐ Elite Trader"
        ),
        Level(
            level_number=6,
            milestone_usd=600.0,
            unlocked_coins=["BTC", "ETH", "SOL", "XRP", "AVAX", "LINK", "DOT", "MATIC",
                           "ADA", "ATOM", "UNI", "AAVE"],
            description="Full portfolio - 12 coins",
            achievement_name="👑 Portfolio King"
        ),
        Level(
            level_number=7,
            milestone_usd=1000.0,
            unlocked_coins=["BTC", "ETH", "SOL", "XRP", "AVAX", "LINK", "DOT", "MATIC",
                           "ADA", "ATOM", "UNI", "AAVE", "LTC", "BCH", "ALGO", "VET"],
            description="Expand to 16 coins - diversify further",
            achievement_name="🚀 Crypto Baron"
        ),
        Level(
            level_number=8,
            milestone_usd=2000.0,
            unlocked_coins=["BTC", "ETH", "SOL", "XRP", "AVAX", "LINK", "DOT", "MATIC",
                           "ADA", "ATOM", "UNI", "AAVE", "LTC", "BCH", "ALGO", "VET",
                           "FIL", "SAND", "MANA", "GRT"],
            description="Full spectrum - 20 coins",
            achievement_name="💰 Wealth Builder"
        )
    ]

    def __init__(self, data_dir: str = "data", starting_balance: float = 59.85):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self.progress_file = os.path.join(data_dir, "progression.json")

        # Load or initialize progression data
        self.data = self._load_progression()

        # If first time, set starting balance
        if self.data["starting_balance"] == 0:
            self.data["starting_balance"] = starting_balance
            self._save_progression()

    # ==================== LEVEL TRACKING ====================

    def get_current_level(self) -> Level:
        """Get current level definition"""
        level_num = self.data["current_level"]
        return self.LEVELS[level_num - 1]

    def get_next_level(self) -> Optional[Level]:
        """Get next level definition"""
        next_num = self.data["current_level"] + 1
        if next_num > len(self.LEVELS):
            return None
        return self.LEVELS[next_num - 1]

    def get_unlocked_coins(self) -> List[str]:
        """Get list of coins currently unlocked for trading"""
        level = self.get_current_level()
        return level.unlocked_coins

    def can_trade_coin(self, coin: str) -> bool:
        """Check if a coin is unlocked at current level"""
        return coin in self.get_unlocked_coins()

    # ==================== PROGRESS TRACKING ====================

    def update_balance(self, current_balance: float) -> Dict:
        """
        Update current balance and check for level ups.

        Returns:
            {
                "leveled_up": bool,
                "new_level": int,
                "achievement": str,
                "unlocked_coins": List[str]
            }
        """
        self.data["current_balance"] = current_balance
        self.data["highest_balance"] = max(self.data["highest_balance"], current_balance)
        self.data["last_updated"] = datetime.now().isoformat()

        # Check for level up
        result = self._check_level_up(current_balance)

        self._save_progression()

        return result

    def _check_level_up(self, balance: float) -> Dict:
        """Check if we've hit the next milestone"""
        current_level = self.data["current_level"]
        next_level = self.get_next_level()

        if next_level is None:
            # Already at max level
            return {
                "leveled_up": False,
                "new_level": current_level,
                "achievement": None,
                "unlocked_coins": []
            }

        # Have we reached the milestone?
        if balance >= next_level.milestone_usd:
            # LEVEL UP!
            self.data["current_level"] = next_level.level_number
            self.data["level_up_history"].append({
                "level": next_level.level_number,
                "timestamp": datetime.now().isoformat(),
                "balance": balance
            })

            # Calculate newly unlocked coins
            old_coins = set(self.get_current_level().unlocked_coins)
            new_coins = set(next_level.unlocked_coins) - old_coins

            return {
                "leveled_up": True,
                "new_level": next_level.level_number,
                "achievement": next_level.achievement_name,
                "unlocked_coins": list(new_coins),
                "description": next_level.description
            }

        return {
            "leveled_up": False,
            "new_level": current_level,
            "achievement": None,
            "unlocked_coins": []
        }

    def get_progress(self) -> Dict:
        """
        Get current progression status.

        Returns detailed progress info for display.
        """
        current_level = self.get_current_level()
        next_level = self.get_next_level()
        current_balance = self.data["current_balance"]

        # Calculate progress percentage
        if next_level:
            # Progress from current milestone to next
            if current_level.level_number == 1:
                start = self.data["starting_balance"]
            else:
                prev_level = self.LEVELS[current_level.level_number - 2]
                start = prev_level.milestone_usd

            target = next_level.milestone_usd
            progress = ((current_balance - start) / (target - start)) * 100
            progress = max(0, min(100, progress))

            needed = target - current_balance
        else:
            # Max level reached
            progress = 100.0
            needed = 0.0

        # Calculate total profit/loss
        profit_loss = current_balance - self.data["starting_balance"]
        profit_loss_pct = (profit_loss / self.data["starting_balance"]) * 100 if self.data["starting_balance"] > 0 else 0

        return {
            "current_level": current_level.level_number,
            "level_name": current_level.achievement_name,
            "current_balance": current_balance,
            "starting_balance": self.data["starting_balance"],
            "highest_balance": self.data["highest_balance"],
            "profit_loss": profit_loss,
            "profit_loss_pct": profit_loss_pct,
            "next_milestone": next_level.milestone_usd if next_level else None,
            "progress_to_next": round(progress, 2),
            "amount_needed": round(needed, 2) if next_level else 0,
            "unlocked_coins": current_level.unlocked_coins,
            "next_unlock": list(set(next_level.unlocked_coins) - set(current_level.unlocked_coins)) if next_level else [],
            "levels_completed": len(self.data["level_up_history"]),
            "max_level": len(self.LEVELS),
            "at_max_level": next_level is None
        }

    # ==================== STATISTICS ====================

    def get_stats(self) -> Dict:
        """Get progression statistics"""
        return {
            "total_levels": len(self.LEVELS),
            "current_level": self.data["current_level"],
            "levels_gained": len(self.data["level_up_history"]),
            "total_coins_unlocked": len(self.get_unlocked_coins()),
            "starting_balance": self.data["starting_balance"],
            "current_balance": self.data["current_balance"],
            "highest_balance": self.data["highest_balance"],
            "total_growth": ((self.data["current_balance"] - self.data["starting_balance"]) / self.data["starting_balance"] * 100) if self.data["starting_balance"] > 0 else 0,
            "level_up_history": self.data["level_up_history"]
        }

    # ==================== PERSISTENCE ====================

    def _load_progression(self) -> Dict:
        """Load progression data from disk"""
        if not os.path.exists(self.progress_file):
            return {
                "current_level": 1,
                "starting_balance": 0,
                "current_balance": 0,
                "highest_balance": 0,
                "level_up_history": [],
                "last_updated": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat()
            }

        with open(self.progress_file, 'r') as f:
            return json.load(f)

    def _save_progression(self):
        """Save progression data to disk"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.data, f, indent=2)


if __name__ == "__main__":
    # Test progression system
    print("🎮 Testing Progression & Level System\n")

    progression = ProgressionSystem(starting_balance=59.85)

    print("📊 Initial Status:")
    progress = progression.get_progress()
    print(f"   Level: {progress['current_level']} - {progress['level_name']}")
    print(f"   Balance: ${progress['current_balance']:.2f}")
    print(f"   Unlocked Coins: {', '.join(progress['unlocked_coins'])}")
    print(f"   Progress to Level {progress['current_level'] + 1}: {progress['progress_to_next']:.1f}%")
    print(f"   Need ${progress['amount_needed']:.2f} more to level up")

    if progress['next_unlock']:
        print(f"   Next Unlock: {', '.join(progress['next_unlock'])}")

    # Simulate reaching Level 2
    print("\n💰 Simulating growth to $90...")
    result = progression.update_balance(90.0)

    if result['leveled_up']:
        print(f"\n🎉 LEVEL UP! You reached Level {result['new_level']}!")
        print(f"   {result['achievement']}")
        print(f"   {result['description']}")
        print(f"   Unlocked: {', '.join(result['unlocked_coins'])}")

    progress = progression.get_progress()
    print(f"\n📊 New Status:")
    print(f"   Level: {progress['current_level']} - {progress['level_name']}")
    print(f"   Balance: ${progress['current_balance']:.2f}")
    print(f"   Profit: ${progress['profit_loss']:.2f} ({progress['profit_loss_pct']:+.1f}%)")
    print(f"   Unlocked Coins: {', '.join(progress['unlocked_coins'])}")
    print(f"   Progress to Level {progress['current_level'] + 1}: {progress['progress_to_next']:.1f}%")
    print(f"   Next Unlock: {', '.join(progress['next_unlock']) if progress['next_unlock'] else 'None'}")

    # Test coin permissions
    print("\n🔒 Coin Access Control:")
    test_coins = ["BTC", "ETH", "SOL", "XRP"]
    for coin in test_coins:
        can_trade = progression.can_trade_coin(coin)
        status = "✅" if can_trade else "🔒"
        print(f"   {status} {coin}: {'UNLOCKED' if can_trade else 'LOCKED'}")

    print("\n✅ Progression system ready - let the game begin!")
