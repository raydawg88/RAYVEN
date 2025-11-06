"""
🌙 Lunar Cycle Tracker

Tracks moon phases and their correlation with trading performance.
Tests the hypothesis that lunar cycles affect cryptocurrency markets.
"""

import datetime
from typing import Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class MoonPhase(Enum):
    """8 distinct moon phases"""
    NEW_MOON = "🌑 New Moon"
    WAXING_CRESCENT = "🌒 Waxing Crescent"
    FIRST_QUARTER = "🌓 First Quarter"
    WAXING_GIBBOUS = "🌔 Waxing Gibbous"
    FULL_MOON = "🌕 Full Moon"
    WANING_GIBBOUS = "🌖 Waning Gibbous"
    LAST_QUARTER = "🌗 Last Quarter"
    WANING_CRESCENT = "🌘 Waning Crescent"


@dataclass
class LunarData:
    """Current lunar cycle information"""
    phase: MoonPhase
    phase_name: str
    day_in_cycle: int  # 0-29
    illumination: float  # 0.0-1.0
    is_full_moon: bool
    is_new_moon: bool
    days_until_full: int
    days_until_new: int


class MoonTracker:
    """
    Calculates current moon phase and provides lunar cycle data.

    Uses astronomical calculations to determine moon phase based on
    known full moon dates and the 29.53-day lunar cycle.
    """

    # Known full moon (reference point)
    REFERENCE_FULL_MOON = datetime.datetime(2025, 1, 13, 22, 27)  # Jan 13, 2025
    LUNAR_CYCLE_DAYS = 29.53059  # Average lunar month

    def __init__(self):
        self.current_phase = None
        self.update()

    def update(self) -> LunarData:
        """Calculate current moon phase"""
        now = datetime.datetime.now()
        self.current_phase = self._calculate_phase(now)
        return self.current_phase

    def _calculate_phase(self, date: datetime.datetime) -> LunarData:
        """
        Calculate moon phase for a given date.

        Algorithm:
        1. Calculate days since reference full moon
        2. Find position in current lunar cycle (0-29.53 days)
        3. Map to 8 phases
        4. Calculate illumination percentage
        """
        # Days since reference full moon
        delta = date - self.REFERENCE_FULL_MOON
        days_since_ref = delta.total_seconds() / 86400

        # Position in current cycle (0-29.53)
        day_in_cycle = days_since_ref % self.LUNAR_CYCLE_DAYS

        # Determine phase
        phase = self._get_phase_from_day(day_in_cycle)

        # Calculate illumination (peaks at full moon)
        # Cosine wave: -1 at new moon (day 0), +1 at full moon (day 14.76)
        illumination = (1 + -1 * (day_in_cycle - self.LUNAR_CYCLE_DAYS / 2) / (self.LUNAR_CYCLE_DAYS / 2)) / 2
        illumination = max(0.0, min(1.0, illumination))

        # Special phase checks
        is_full_moon = 13.5 <= day_in_cycle <= 15.5
        is_new_moon = day_in_cycle <= 1.5 or day_in_cycle >= 28.0

        # Days until next full/new
        if day_in_cycle < 14.76:
            days_until_full = int(14.76 - day_in_cycle)
        else:
            days_until_full = int(self.LUNAR_CYCLE_DAYS - day_in_cycle + 14.76)

        if day_in_cycle < 0.5:
            days_until_new = int(self.LUNAR_CYCLE_DAYS - day_in_cycle)
        else:
            days_until_new = int(self.LUNAR_CYCLE_DAYS - day_in_cycle)

        return LunarData(
            phase=phase,
            phase_name=phase.value,
            day_in_cycle=int(day_in_cycle),
            illumination=illumination,
            is_full_moon=is_full_moon,
            is_new_moon=is_new_moon,
            days_until_full=days_until_full,
            days_until_new=days_until_new
        )

    def _get_phase_from_day(self, day: float) -> MoonPhase:
        """Map day in cycle to moon phase"""
        if day <= 1.84:
            return MoonPhase.NEW_MOON
        elif day <= 5.53:
            return MoonPhase.WAXING_CRESCENT
        elif day <= 9.23:
            return MoonPhase.FIRST_QUARTER
        elif day <= 12.91:
            return MoonPhase.WAXING_GIBBOUS
        elif day <= 16.61:
            return MoonPhase.FULL_MOON
        elif day <= 20.30:
            return MoonPhase.WANING_GIBBOUS
        elif day <= 23.99:
            return MoonPhase.LAST_QUARTER
        else:
            return MoonPhase.WANING_CRESCENT

    def get_phase_description(self) -> str:
        """Get human-readable description of current phase"""
        lunar_data = self.current_phase or self.update()

        descriptions = {
            MoonPhase.NEW_MOON: "New beginnings, fresh starts, planting seeds",
            MoonPhase.WAXING_CRESCENT: "Growth phase, momentum building",
            MoonPhase.FIRST_QUARTER: "Action phase, decisions and challenges",
            MoonPhase.WAXING_GIBBOUS: "Refinement phase, nearing peak",
            MoonPhase.FULL_MOON: "Peak energy, culmination, maximum visibility",
            MoonPhase.WANING_GIBBOUS: "Reflection phase, sharing wisdom",
            MoonPhase.LAST_QUARTER: "Release phase, letting go",
            MoonPhase.WANING_CRESCENT: "Rest phase, contemplation"
        }

        return descriptions.get(lunar_data.phase, "Unknown phase")

    def get_trading_bias(self) -> Dict[str, any]:
        """
        Get initial trading bias based on moon phase.

        Note: This is a HYPOTHESIS to be tested. The system will learn
        whether these biases are actually predictive over time.
        """
        lunar_data = self.current_phase or self.update()

        # Initial hypotheses (to be validated by data)
        biases = {
            MoonPhase.FULL_MOON: {
                "bias": "BULLISH",
                "confidence_modifier": 0.10,  # +10% to confidence
                "reasoning": "Testing hypothesis: Full moon = peak energy, bullish"
            },
            MoonPhase.NEW_MOON: {
                "bias": "BULLISH",
                "confidence_modifier": 0.05,  # +5% to confidence
                "reasoning": "Testing hypothesis: New moon = fresh starts, bullish"
            },
            MoonPhase.FIRST_QUARTER: {
                "bias": "CAUTION",
                "confidence_modifier": -0.05,  # -5% from confidence
                "reasoning": "Testing hypothesis: First quarter = challenges, caution"
            },
            MoonPhase.LAST_QUARTER: {
                "bias": "CAUTION",
                "confidence_modifier": -0.05,  # -5% from confidence
                "reasoning": "Testing hypothesis: Last quarter = release, caution"
            }
        }

        return biases.get(
            lunar_data.phase,
            {"bias": "NEUTRAL", "confidence_modifier": 0.0, "reasoning": "No lunar bias for this phase"}
        )

    def format_display(self) -> str:
        """Format lunar data for console display"""
        lunar_data = self.current_phase or self.update()
        bias = self.get_trading_bias()

        return f"""
╔════════════════════════════════════════════════════════════╗
║  🌙 LUNAR CYCLE STATUS                                     ║
╚════════════════════════════════════════════════════════════╝

Current Phase: {lunar_data.phase_name}
Day in Cycle: {lunar_data.day_in_cycle}/29
Illumination: {lunar_data.illumination*100:.1f}%

Description: {self.get_phase_description()}

Trading Bias: {bias['bias']}
Confidence Modifier: {bias['confidence_modifier']:+.1%}
Reasoning: {bias['reasoning']}

Next Full Moon: {lunar_data.days_until_full} days
Next New Moon: {lunar_data.days_until_new} days

Note: Lunar correlations are being tested empirically.
System will adapt based on actual trading results.
╚════════════════════════════════════════════════════════════╝
        """.strip()


if __name__ == "__main__":
    # Test the moon tracker
    tracker = MoonTracker()
    print(tracker.format_display())

    # Show lunar data object
    print("\nLunar Data:")
    print(f"  Phase: {tracker.current_phase.phase_name}")
    print(f"  Day: {tracker.current_phase.day_in_cycle}")
    print(f"  Illumination: {tracker.current_phase.illumination:.2%}")
    print(f"  Full Moon: {tracker.current_phase.is_full_moon}")
    print(f"  New Moon: {tracker.current_phase.is_new_moon}")
