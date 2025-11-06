# 🔍 RAYVEN Data Sources & Research Architecture

## Philosophy: Research-Sound, Minimal APIs, Maximum Context

Every trade must be backed by:
1. **Technical Evidence** (price action, volume, indicators)
2. **Market Context** (sentiment, news, trends)
3. **Pattern History** (has this setup worked before?)
4. **Lunar Phase** (empirical correlation testing)

---

## Data Architecture

### **Tier 1: Essential Trading Data (Coinbase API)**

**Purpose:** Prices, execution, your balance
**Frequency:** Every 5 minutes (scanning), real-time (execution)
**API Key Required:** Yes (you have this)

**Endpoints Used:**
```
GET /api/v3/brokerage/products/{pair}/ticker    # Current price
GET /api/v3/brokerage/products/{pair}/candles   # Historical OHLCV
GET /api/v3/brokerage/accounts                  # Your balance
POST /api/v3/brokerage/orders                   # Place trades
GET /api/v3/brokerage/orders/historical/fills   # Trade history
```

**What We Calculate Ourselves:**
- RSI (Relative Strength Index)
- Moving Averages (MA20, MA50, MA200)
- Support/Resistance levels
- Volume ratios
- Bollinger Bands
- MACD

**Rationale:** We're already paying Coinbase fees, use their data. Self-calculated indicators are more reliable than third-party APIs.

---

### **Tier 2: Market Context (WebFetch - No API Keys)**

**Purpose:** Sentiment, news, macro context
**Frequency:** On-demand (only when considering a trade)
**API Key Required:** No - public web scraping

#### **Source 1: Fear & Greed Index**
- **URL:** https://alternative.me/crypto/fear-and-greed-index/
- **Data:** Market sentiment score (0-100)
- **Usage:** Daily check, affects position sizing
- **WebFetch Prompt:** "What is the current crypto fear and greed index score and what does it indicate?"

**Example:**
```python
# Before trading day starts
sentiment = web_fetch("https://alternative.me/crypto/fear-and-greed-index/",
                      "Current fear greed score and market sentiment")
# If "Extreme Fear" (score < 20) → Increase buy confidence
# If "Extreme Greed" (score > 80) → Reduce buy confidence
```

#### **Source 2: CoinMarketCap Trending**
- **URL:** https://coinmarketcap.com/
- **Data:** Trending coins, top gainers/losers
- **Usage:** When considering which coin to trade
- **WebFetch Prompt:** "What are the top 3 trending cryptocurrencies and why?"

#### **Source 3: Bitcoin Dominance**
- **URL:** https://www.tradingview.com/symbols/CRYPTOCAP-BTC.D/
- **Data:** BTC dominance percentage
- **Usage:** Decide if it's "altcoin season" or "BTC season"
- **WebFetch Prompt:** "What is Bitcoin dominance percentage and is it rising or falling?"

**Logic:**
- BTC dominance rising → Trade BTC only
- BTC dominance falling → Safe to trade altcoins (ETH, SOL)

#### **Source 4: Crypto News (Major Events Only)**
- **URL:** https://cryptopanic.com/
- **Data:** Breaking news, major announcements
- **Usage:** Check for "black swan" events before trading
- **WebFetch Prompt:** "Any major Bitcoin or cryptocurrency news in the last 4 hours?"

**Example:**
```python
# Before executing a BTC buy
news = web_fetch("https://cryptopanic.com/",
                 "Any major negative Bitcoin news in last 4 hours?")
if "hack" in news or "regulation" in news or "ban" in news:
    # Skip trade, wait for clarity
```

#### **Source 5: Liquidation Data**
- **URL:** https://www.coinglass.com/LiquidationData
- **Data:** Long/short liquidations
- **Usage:** Identify potential reversal points
- **WebFetch Prompt:** "Are there significant liquidations happening in BTC? Long or short?"

**Logic:**
- Massive long liquidations → Potential buy opportunity (oversold)
- Massive short liquidations → Potential sell opportunity (overbought)

---

### **Tier 3: Technical Research (Self-Generated)**

**Purpose:** Build library of proven patterns
**Format:** Markdown files in `/research/`
**No External Data:** Pure observation and testing

#### **Pattern Library Structure:**

```
research/
├── patterns/
│   ├── support_bounce.md
│   ├── resistance_fade.md
│   ├── volume_breakout.md
│   ├── rsi_divergence.md
│   └── range_exhaustion.md
├── lunar/
│   ├── full_moon_analysis.md
│   ├── new_moon_analysis.md
│   └── quarter_moon_analysis.md
└── coins/
    ├── btc_profile.md
    ├── eth_profile.md
    └── sol_profile.md
```

**Example Pattern File (support_bounce.md):**
```markdown
# Support Bounce Pattern

## Description
Buying when price reaches bottom 20% of daily range with volume confirmation.

## Entry Criteria
- Price at 0-20% of 8-hour range
- Volume > 1.5x average
- RSI < 40
- Not in strong downtrend (price > 4h MA)

## Exit Strategy
- Take Profit 1: +3%
- Take Profit 2: +5%
- Stop Loss: -2.5%

## Historical Performance
- Trades: 47
- Win Rate: 68.1%
- Avg Win: +3.4%
- Avg Loss: -2.1%
- Risk/Reward: 1.6:1

## Best Conditions
- Works best during 6am-10am EST
- Full moon correlation: +15% win rate boost
- Fails during strong downtrends

## Last Updated
2025-01-06 - Added lunar correlation data
```

---

### **Tier 4: Lunar Cycle (Self-Calculated)**

**Purpose:** Test hypothesis that moon phases affect crypto
**Data Source:** Astronomical calculation (no external API)
**File:** `/src/lunar/moon_tracker.py` (already built)

**Current Hypotheses to Test:**
- Full Moon = Bullish (+10% confidence)
- New Moon = Bullish (+5% confidence)
- Quarter Moons = Caution (-5% confidence)

**Validation:** After 50+ trades, statistical analysis determines if correlation is real.

---

## Data Flow Per Trade Decision

```
[SCAN TRIGGER] Every 5 minutes
    ↓
[1] Fetch BTC Price & Volume (Coinbase API)
    ↓
[2] Calculate Technicals (RSI, MAs, Range Position)
    ↓
[3] Check Moon Phase (Self-calculated)
    ↓
[4] Pattern Match (Is this a known setup?)
    ↓

[IF POTENTIAL TRADE FOUND]
    ↓
[5] WebFetch: Fear & Greed Index (1 call)
    ↓
[6] WebFetch: Recent BTC News (1 call)
    ↓
[7] WebFetch: Liquidation Data (1 call)
    ↓

[DECISION ENGINE]
├─ Technical Score: 0-100
├─ Lunar Modifier: -5% to +10%
├─ Sentiment Modifier: -10% to +10%
├─ News Filter: BLOCK if negative
└─ Final Confidence: 0-100%

[IF Confidence > 75%]
    ↓
[EXECUTE TRADE] (Coinbase API)
    ↓
[LOG EVERYTHING] (for learning)
```

**Total API/WebFetch Calls Per Trade:**
- Coinbase API: 2 calls (price + execute)
- WebFetch: 3 calls (sentiment, news, liquidations)
- **Total: 5 calls per trade**

**Daily Estimates:**
- Scanning: 288 Coinbase calls/day (every 5 min)
- Trading: ~3-5 trades/day = 15-25 calls/day
- **Total: ~300 calls/day (well under limits)**

---

## Why This Approach is Research-Sound

### 1. **Multiple Data Perspectives**
- Technical (price/volume)
- Sentiment (fear/greed)
- News (events)
- Liquidity (liquidations)
- Lunar (hypothesis testing)

### 2. **Verification Layers**
Every trade must pass:
- Technical setup ✓
- Pattern history ✓
- Sentiment check ✓
- News filter ✓
- Lunar correlation ✓

### 3. **Learning System**
- Tracks which patterns work
- Validates lunar hypothesis
- Adapts to what succeeds
- Eliminates what fails

### 4. **Minimal External Dependencies**
- 1 API (Coinbase - required anyway)
- 3-5 WebFetch sources (public data)
- No paid subscriptions
- No rate limit concerns

### 5. **Explainable Decisions**
Every trade logs:
```
WHY: Support bounce pattern (68% historical win rate)
TECHNICAL: RSI 34, bottom 18% of range, 2.1x volume
SENTIMENT: Fear & Greed at 35 (Fear - contrarian buy)
NEWS: No negative events
LUNAR: New Moon (+5% confidence boost)
CONFIDENCE: 82% (Execute)
```

---

## Future Expansion (Level 3+)

When capital grows, can add:
- **On-chain metrics** (whale movements) - Via WebFetch of Glassnode/IntoTheBlock
- **Social sentiment** (Twitter volume) - Via WebFetch of LunarCrush
- **Exchange flows** (in/out of exchanges) - Via WebFetch of CryptoQuant
- **Funding rates** (futures sentiment) - Via WebFetch of Coinglass

But start minimal. Prove edge with simple data first.

---

## Rate Limits & Costs

| Source | Calls/Day | Limit | Cost |
|--------|-----------|-------|------|
| Coinbase API | 300 | 10,000 | Free |
| WebFetch (Fear/Greed) | 1-3 | None | Free |
| WebFetch (News) | 5-10 | None | Free |
| WebFetch (Liquidations) | 3-5 | None | Free |
| Moon Tracker | Unlimited | None | Free |

**Total Cost: $0/month** (except trading fees)

---

## Implementation Priority

**Phase 1 (Level 1 - BTC Only):**
1. ✅ Coinbase API integration
2. ✅ Self-calculated technicals
3. ✅ Moon phase tracker
4. ⏳ WebFetch: Fear & Greed
5. ⏳ WebFetch: News check
6. ⏳ Pattern library (build as we learn)

**Phase 2 (Level 2-3):**
7. WebFetch: Liquidation data
8. WebFetch: BTC dominance
9. Expanded pattern library
10. Lunar correlation validation

**Phase 3 (Level 4+):**
11. On-chain metrics
12. Social sentiment
13. Multi-coin intelligence profiles

---

**Summary:** Research-sound = Multiple perspectives + Pattern validation + Explainable decisions + Empirical learning. We achieve this with 1 API + WebFetch + self-calculation.
