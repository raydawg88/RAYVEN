# 🤖 RAYVEN - Reinforcement Learning Crypto Trader

An intelligent cryptocurrency trading bot that learns and evolves like a player in a game.

## 🎮 The Game

RAYVEN is built like a game where the "player" (AI) learns to trade crypto by progressing through levels. Each level unlocks new coins to trade, creating a natural learning progression from simple (BTC only) to complex (20+ coins).

**Current Status**: Fully operational with live trading capabilities.

## 🎯 The Progression System

### Level Milestones

| Level | Target Balance | Unlocked Coins | Achievement |
|-------|---------------|----------------|-------------|
| 1 | $85 | BTC | 🥉 Bitcoin Apprentice |
| 2 | $120 | BTC, ETH | 🥈 Dual Asset Trader |
| 3 | $180 | BTC, ETH, SOL | 🥇 Triple Threat |
| 4 | $270 | + XRP, AVAX | 💎 Multi-Asset Master |
| 5 | $400 | + LINK, DOT, MATIC | ⭐ Elite Trader |
| 6 | $600 | + ADA, ATOM, UNI, AAVE | 👑 Portfolio King |
| 7 | $1000 | + LTC, BCH, ALGO, VET | 🚀 Crypto Baron |
| 8 | $2000 | + FIL, SAND, MANA, GRT | 💰 Wealth Builder |

Start with $60, trade BTC only. Hit $85, level up and unlock ETH. Keep growing!

## 🧠 How It Learns

### Reinforcement Learning
- Tries different trading patterns (support bounce, mean reversion, trend follow, etc.)
- Tracks which patterns work best (win rates, avg profit)
- Gradually improves strategy based on real outcomes
- Balances exploration (trying new things) with exploitation (using what works)

### Pattern Memory
- Records every trade with full context (RSI, price position, moon phase, sentiment)
- Calculates pattern statistics (support_bounce: 68% win rate, +3.2% avg profit)
- Learns coin-specific behaviors
- Identifies best entry/exit conditions

### Moon Phase Correlation
- Tracks trades during each moon phase
- Calculates statistical edge (Full Moon: +8% vs baseline)
- Adjusts confidence based on learned correlations
- Tests the hypothesis: Do lunar cycles affect crypto?

## 📊 Core Components

### 1. Market Analysis
- **Technical Analysis**: RSI, Moving Averages, Support/Resistance, Volume, Trends
- **Market Intelligence**: Fear/Greed Index, BTC Dominance, News Sentiment, Liquidations
- **Lunar Analysis**: Moon phase, illumination %, trading bias

### 2. Decision Engine
- Pattern detection from technical indicators
- Confidence scoring (min 65% to act)
- Position sizing based on Kelly Criterion
- Risk management (high/medium/low risk levels)

### 3. Memory System
- Trade history with outcomes
- Pattern win rates and statistics
- Lunar correlation tracking
- Lessons learned generator

### 4. Progression Tracker
- Current level and balance
- Progress to next milestone
- Unlocked coins and access control
- Achievement history

### 5. Live Dashboard
- Real-time market analysis
- Current decision with reasoning
- Learning insights and lessons
- Trade logs and outcomes

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Coinbase Advanced Trade account
- API credentials from [Coinbase Cloud Platform](https://cloud.coinbase.com/)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/raydawg88/RAYVEN.git
cd RAYVEN
```

2. **Create credentials file**
```bash
mkdir credentials
nano credentials/.env
```

Add your Coinbase API credentials:
```
COINBASE_API_KEY_NAME=organizations/.../apiKeys/...
COINBASE_PRIVATE_KEY=-----BEGIN EC PRIVATE KEY-----...
COINBASE_PROJECT_ID=your-project-id
```

3. **Run with web interface** (90s retro visualization!) 🎮
```bash
./start_web.sh --dry-run
```
Opens http://localhost:5001 in your browser automatically.

4. **Or run in terminal** (classic log view)
```bash
./start.sh --dry-run
```

5. **Go live** (real money!)
```bash
./start_web.sh  # or ./start.sh
```

## 🎮 Web Interface

**NEW**: RAYVEN now has a 90s retro web interface!

Instead of scrolling logs, watch your trades come alive in a contribution graph style visualization with CRT scanlines, neon colors, and pulsing animations.

### Features
- **9-Step Cycle Grid**: Watch each step of the trading process light up
- **Trade History Grid**: Contribution-style squares (green=win, red=loss)
- **Live Progress Bar**: Rainbow glow shows progress to next level
- **Level-Up Animation**: Screen flashes rainbow when you level up
- **CRT Effects**: Scanlines and screen curvature for authentic 90s feel
- **Status Log**: See what RAYVEN is thinking in real-time
- **Tooltips**: Hover over trade squares to see details

### Screenshots
```
╔════════════════════════════════════════════════════╗
║ 💾 RAYVEN.EXE v1.0          LVL 1  ████████░░  68% ║
╠════════════════════════════════════════════════════╣
║  TRADING: BTC                      BAL: $62.50    ║
║                                                    ║
║  CURRENT CYCLE                                     ║
║  [█][█][█][█][█][█][⚡][░][░]  ← Step 7/9         ║
║                                                    ║
║  TRADE HISTORY                                     ║
║  [█][█][█][█][█][█][█][█][█][█]                   ║
║  [█][█][█][█][█][█][█][█][█][█]                   ║
║                                                    ║
║  > Analyzing market... RSI oversold detected      ║
╚════════════════════════════════════════════════════╝
```

Much more engaging than scrolling text!

## 📁 Project Structure

```
RAYVEN/
├── main.py                     # Main orchestrator (terminal)
├── main_web.py                 # Main orchestrator (web interface)
├── start.sh                    # Startup script (terminal)
├── start_web.sh                # Startup script (web)
├── requirements.txt            # Dependencies
│
├── src/
│   ├── api/
│   │   └── exchange.py         # Coinbase API wrapper
│   │
│   ├── lunar/
│   │   └── moon_tracker.py     # Moon phase calculations
│   │
│   ├── analysis/
│   │   └── technicals.py       # Technical indicators
│   │
│   ├── intelligence/
│   │   └── market_intel.py     # Market sentiment & context
│   │
│   ├── core/
│   │   ├── memory.py           # Learning & trade history
│   │   └── progression.py      # Level system
│   │
│   ├── strategy/
│   │   └── trading_engine.py   # RL decision-making
│   │
│   └── interface/
│       └── dashboard.py        # Terminal UI
│
├── web/                        # 90s retro web interface
│   ├── app.py                  # Flask server + WebSocket
│   ├── templates/
│   │   └── index.html          # Main page
│   └── static/
│       ├── style.css           # 90s retro styling
│       └── app.js              # Grid animations
│
├── data/                       # Auto-generated, gitignored
│   ├── trades.json            # Trade history
│   ├── patterns.json          # Pattern statistics
│   ├── lunar_correlations.json # Moon phase data
│   └── progression.json       # Level progress
│
└── credentials/               # Private, gitignored
    └── .env                   # API credentials
```

## 🎯 Trading Strategy

### Mean Reversion Focus
Primary strategy: Buy dips, sell rips within established ranges.

**Buy Signals:**
- RSI < 30 (oversold)
- Price near support (bottom 25% of range)
- Support bounce pattern
- Bullish moon phase (if learned correlation)

**Sell Signals:**
- RSI > 70 (overbought)
- Price near resistance (top 25% of range)
- Resistance rejection pattern
- Bearish moon phase (if learned correlation)

### Position Sizing
- Low risk: 30% of capital
- Medium risk: 25% of capital
- High risk: 15% of capital
- Adjusted by confidence level (Kelly-inspired)

### Learning Parameters
- Exploration rate: 15% (occasionally tries suboptimal patterns to learn)
- Min confidence: 65% (won't trade unless 65%+ confident)
- Pattern min trades: 3 (needs 3+ trades before trusting pattern stats)
- Loop interval: 60 seconds (checks market every minute)

## 📈 Example Session

```
🤖 RAYVEN - Reinforcement Learning Crypto Trader

📊 STATUS
Level: 1 - 🥉 Bitcoin Apprentice
Balance: $59.85 | P/L: $0.00 (0.0%)
Progress: [░░░░░░░░░░░░░░░░░░░░] 0.0%
Next Level: $85.00 ($25.15 to go)
Unlocked Coins: BTC

🔍 MARKET ANALYSIS - BTC
Price: $101,234.56
📊 RSI: 32.5 🔴 OVERSOLD
🎯 Range Position: 24% (near support)
📈 Trend: UPTREND (moderate)
🌐 Sentiment: NEUTRAL (55%)
🌙 Moon: First Quarter (52% illuminated)

🎯 DECISION
Action: 💰 BUY
Confidence: 68% ✓
Pattern: Support Bounce
Risk: MEDIUM

💭 Reasoning:
   • Near support (24%) + RSI oversold (32)
   • Historical: 65% win rate
   • Moon phase First Quarter (+3% edge)

📈 Expected: +2-5%
💵 Position Size: $14.96

[12:40:53] 💰 BUY 0.00014800 BTC @ $101,234.56
           Reason: Support bounce pattern

[Iteration 1] Waiting 60s until next check...
```

## 🔒 Safety & Risk Management

- **Dry-run mode**: Test without risking real money
- **Progressive unlocking**: Can't trade locked coins
- **Position limits**: Max 30% per trade
- **Confidence threshold**: Min 65% to execute
- **Pattern validation**: Needs 3+ trades before trusting
- **Full transparency**: See every decision with reasoning

## 📚 Learning Insights

After each session, RAYVEN generates insights:

```
📚 LEARNING INSIGHTS
Total Trades: 15
Win Rate: 66.7%
Total Profit: +8.3%

✅ Best Patterns:
   • Support Bounce (72% WR, +4.2% avg)
   • Mean Reversion (64% WR, +2.8% avg)

❌ Avoid Patterns:
   • Breakout (38% WR, -1.5% avg)

🌙 Moon Phase Insights:
   • Full Moon: +12% edge (high confidence)
   • New Moon: +8% edge (medium confidence)

📖 Lessons Learned:
   ✅ Support bounce works well in uptrends
   🌙 Full Moon shows +12% edge
   📚 Keep trading to refine breakout strategy
```

## 🛠️ Development

### Adding New Patterns
Edit `src/strategy/trading_engine.py` → `_detect_patterns()`:
```python
if your_condition:
    patterns.append({
        "pattern": TradingPattern.YOUR_PATTERN,
        "direction": "buy",  # or "sell"
        "confidence": 0.70,
        "reason": "Why this pattern triggers",
        "historical_wr": 65.0
    })
```

### Adding New Indicators
Edit `src/analysis/technicals.py`:
```python
@staticmethod
def calculate_your_indicator(data):
    # Your logic here
    return result
```

### Adding Intelligence Sources
Edit `src/intelligence/market_intel.py` → Add new data fetching methods

## 🤝 Contributing

This is a personal trading project, but ideas are welcome! Open an issue to discuss.

## ⚠️ Disclaimer

**RAYVEN is experimental software for educational purposes.**

- Cryptocurrency trading is extremely risky
- You can lose all your money
- Past performance doesn't guarantee future results
- No warranties or guarantees provided
- Use at your own risk
- Not financial advice

Only trade with money you can afford to lose completely.

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

Built with:
- [Coinbase Advanced Trade API](https://docs.cloud.coinbase.com/advanced-trade-api/)
- Python 3.13
- A lot of coffee

---

**Remember**: The goal is learning and growth, not overnight riches. Trade responsibly! 🚀
