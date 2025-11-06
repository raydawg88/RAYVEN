# 🏗️ RAYVEN Architecture: Multi-Source Intelligence System

## Design Philosophy

**"Triple Source Validation"** - Every trade decision uses 3 types of data sources:
1. **API** - Real-time trading data (Coinbase)
2. **WebFetch** - Public intelligence (sentiment, news, metrics)
3. **MCP** - Structured tool access (market data, calculations)

---

## Data Source Mix (Starting Day 1)

### **🔌 API Layer: Coinbase Advanced Trade**

**Purpose:** Trading execution & price data
**Implementation:** Direct REST API with JWT auth
**File:** `/src/api/coinbase_client.py`

```python
Endpoints:
- GET /products/{pair}/ticker      # Real-time price
- GET /products/{pair}/candles     # OHLCV data
- GET /accounts                    # Balance
- POST /orders                     # Execute trades
- GET /orders/historical/fills     # Trade history
```

**Why API Here:** Need authentication, need reliability, need execution.

---

### **🌐 WebFetch Layer: Market Intelligence**

**Purpose:** Sentiment, news, public metrics
**Implementation:** WebFetch tool (built into Claude Code)
**Files:** `/src/intelligence/web_sources.py`

#### **WebFetch Sources (Day 1):**

**1. Fear & Greed Index**
```python
url = "https://alternative.me/crypto/fear-and-greed-index/"
prompt = "Current fear/greed score and market sentiment"
use = "Position sizing modifier"
frequency = "Daily (8am)"
```

**2. CryptoP panic News**
```python
url = "https://cryptopanic.com/"
prompt = "Major BTC/crypto news in last 4 hours, any negative events?"
use = "Trade blocking (if negative news)"
frequency = "Before each trade"
```

**3. Bitcoin Dominance**
```python
url = "https://www.tradingview.com/symbols/CRYPTOCAP-BTC.D/"
prompt = "BTC dominance %, rising or falling trend?"
use = "Decide BTC-only vs altcoin trading"
frequency = "Daily (8am)"
```

**4. Liquidation Heatmap**
```python
url = "https://www.coinglass.com/LiquidationData"
prompt = "Recent BTC liquidations, long or short side?"
use = "Reversal opportunity detection"
frequency = "Before each trade"
```

**5. CoinMarketCap BTC Page**
```python
url = "https://coinmarketcap.com/currencies/bitcoin/"
prompt = "BTC 24h trend, volume analysis, any alerts?"
use = "Quick market context check"
frequency = "Every scan cycle (5 min)"
```

**Why WebFetch:** No API keys, no rate limits, fresh public data, sentiment/news.

---

### **🔧 MCP Layer: Structured Tools**

**Purpose:** Calculations, formatted data, reusable tools
**Implementation:** Custom MCP servers + community servers

#### **MCP Server 1: RAYVEN Technical Analysis** (Custom - We Build This)

**What It Provides:**
```
Tools:
- calculate_rsi(prices: list, period: int) → float
- calculate_moving_average(prices: list, period: int) → float
- detect_support_resistance(prices: list) → dict
- calculate_range_position(current: float, high: float, low: float) → float
- detect_volume_spike(volumes: list) → bool
```

**Why MCP:**
- Reusable across agents
- Standardized calculations
- Easy to test/validate
- Can be used by other projects later

**Implementation:**
```bash
# We'll build this as a simple Python MCP server
/mcp/
├── rayven_technical_mcp/
│   ├── server.py
│   ├── indicators.py
│   └── manifest.json
```

#### **MCP Server 2: Fetch MCP** (Use Existing)

**What It Provides:**
- Structured web scraping
- HTML parsing
- JSON extraction from pages

**Use Case:**
Instead of raw WebFetch, MCP can parse specific elements:
```python
# WebFetch returns full page text
raw_text = web_fetch(url, prompt)

# MCP Fetch returns structured data
data = mcp_fetch.get_json_from_page(
    url="https://api.alternative.me/fng/",
    selector=".fng-value"
)
# Returns: {"value": 42, "classification": "Fear"}
```

**Setup:**
```bash
# Install community fetch MCP
npm install -g @modelcontextprotocol/server-fetch
```

#### **MCP Server 3: Memory MCP** (Use Existing)

**What It Provides:**
- Persistent storage
- Key-value store
- Pattern database

**Use Case:**
Store learned patterns and trade history:
```python
# Store pattern performance
mcp_memory.set("pattern:support_bounce:win_rate", 0.682)
mcp_memory.set("lunar:full_moon:trades", [trade1, trade2, ...])

# Retrieve for decision making
win_rate = mcp_memory.get("pattern:support_bounce:win_rate")
```

---

## Decision Flow: Triple Source Validation

```
[TRADE SIGNAL DETECTED]
    ↓
┌─────────────────────────────────────────┐
│ SOURCE 1: API (Coinbase)                │
├─────────────────────────────────────────┤
│ • Current BTC price: $43,850            │
│ • 24h volume: $28.5B                    │
│ • Recent candles: [OHLCV data]          │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ SOURCE 2: MCP (Technical Analysis)      │
├─────────────────────────────────────────┤
│ • RSI: 34 (oversold) ✓                  │
│ • Range position: 18% (near support) ✓  │
│ • Volume spike: 2.1x detected ✓         │
│ • Support level: $43,800 ✓              │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ SOURCE 3: WebFetch (Market Context)     │
├─────────────────────────────────────────┤
│ • Fear/Greed: 38 (Fear) ✓               │
│ • News: No major negative events ✓      │
│ • Liquidations: $120M longs just        │
│   liquidated (reversal signal) ✓        │
│ • BTC Dominance: 54%, stable            │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ SOURCE 4: MCP Memory (Pattern History)  │
├─────────────────────────────────────────┤
│ • Support bounce win rate: 68.2%        │
│ • Current moon phase: New Moon          │
│ • Historical moon edge: +5%             │
└─────────────────────────────────────────┘
    ↓
[CONFIDENCE CALCULATION]
├─ Technical (API + MCP): 75/100
├─ Sentiment (WebFetch): +10 points
├─ Pattern History (MCP): +8 points
├─ Lunar Phase: +5 points
└─ FINAL: 98/100 ✓ EXECUTE

[TRADE EXECUTION via API]
```

---

## Implementation Roadmap

### **Phase 1: Foundation (Week 1)**

```python
# 1. Coinbase API Client
/src/api/coinbase_client.py
- JWT authentication
- Price fetching
- Order execution

# 2. WebFetch Intelligence
/src/intelligence/web_sources.py
- Fear/Greed scraper
- News checker
- Liquidation monitor

# 3. Custom Technical MCP
/mcp/rayven_technical_mcp/
- RSI calculation
- Range detection
- Volume analysis
```

### **Phase 2: Enhancement (Week 2)**

```python
# 4. Install Community MCPs
npm install -g @modelcontextprotocol/server-fetch
npm install -g @modelcontextprotocol/server-memory

# 5. Integrate MCP Memory
- Store trade history
- Track pattern performance
- Lunar correlation database

# 6. Advanced WebFetch
- Multiple news sources
- Sentiment aggregation
- Social media signals
```

### **Phase 3: Optimization (Week 3+)**

```python
# 7. Build additional custom MCPs
- Coinbase MCP wrapper (cleaner API interface)
- Pattern recognition MCP
- Risk calculation MCP

# 8. Expand WebFetch sources
- On-chain metrics (Glassnode)
- Exchange flows (CryptoQuant)
- Funding rates (Coinglass)
```

---

## Why This Mix Works

### **API Strengths:**
- ✅ Authentication
- ✅ Real-time execution
- ✅ Reliable price data
- ✅ Account management

### **WebFetch Strengths:**
- ✅ No API keys needed
- ✅ Fresh sentiment data
- ✅ News and context
- ✅ Public metrics

### **MCP Strengths:**
- ✅ Reusable tools
- ✅ Structured data
- ✅ Cross-agent sharing
- ✅ Persistent memory
- ✅ Standardized calculations

### **Together:**
**API** gives us trading power, **WebFetch** gives us market intelligence, **MCP** gives us computation and memory. Each handles what it's best at.

---

## Configuration

**File:** `/config/sources.json`
```json
{
  "api": {
    "coinbase": {
      "enabled": true,
      "base_url": "https://api.coinbase.com",
      "auth_method": "jwt",
      "credentials_path": "../RAYVEN 2/credentials/.env"
    }
  },
  "webfetch": {
    "enabled": true,
    "sources": [
      {
        "name": "fear_greed",
        "url": "https://alternative.me/crypto/fear-and-greed-index/",
        "frequency": "daily",
        "prompt": "Current fear greed index score and sentiment"
      },
      {
        "name": "news",
        "url": "https://cryptopanic.com/",
        "frequency": "per_trade",
        "prompt": "Major BTC news last 4 hours, negative events?"
      },
      {
        "name": "liquidations",
        "url": "https://www.coinglass.com/LiquidationData",
        "frequency": "per_trade",
        "prompt": "Recent BTC liquidations, which side?"
      }
    ]
  },
  "mcp": {
    "enabled": true,
    "servers": [
      {
        "name": "rayven_technical",
        "type": "custom",
        "path": "./mcp/rayven_technical_mcp",
        "tools": ["calculate_rsi", "detect_range", "volume_spike"]
      },
      {
        "name": "fetch",
        "type": "community",
        "package": "@modelcontextprotocol/server-fetch"
      },
      {
        "name": "memory",
        "type": "community",
        "package": "@modelcontextprotocol/server-memory",
        "config": {
          "storage_path": "./data/mcp_memory.db"
        }
      }
    ]
  }
}
```

---

## Logging Output Example

```
[2025-01-06 14:32:15] 🔍 SCANNING BTC
╔════════════════════════════════════════════════════════════╗
║  TRIPLE SOURCE VALIDATION                                  ║
╚════════════════════════════════════════════════════════════╝

📡 API SOURCE: Coinbase
  ├─ BTC Price: $43,850
  ├─ 24h Volume: $28.5B
  ├─ 24h High/Low: $44,500 / $43,200
  └─ Data Quality: ✅ EXCELLENT

🔧 MCP SOURCE: Technical Analysis
  ├─ RSI: 34 (oversold) ✅
  ├─ Range Position: 18% (near support) ✅
  ├─ Volume Spike: 2.1x average ✅
  ├─ MA20: $44,100 (below, bearish context) ⚠️
  └─ Support Level: $43,800 (price testing)

🌐 WEBFETCH SOURCE: Market Intelligence
  ├─ Fear/Greed Index: 38 (Fear) ✅
  │   └─ Contrarian signal: Buy when others fearful
  ├─ News Check: No major negative events ✅
  ├─ Liquidations: $120M longs liquidated ✅
  │   └─ Oversold bounce likely
  └─ BTC Dominance: 54% (stable, safe to trade)

💾 MCP MEMORY: Pattern Database
  ├─ Pattern: Support Bounce
  ├─ Historical Win Rate: 68.2% (47 trades)
  ├─ Best Conditions: Fear + Liquidations + RSI<40
  └─ 🌙 Lunar Correlation: New Moon (+5% edge)

═══════════════════════════════════════════════════════════
📊 CONFIDENCE CALCULATION
═══════════════════════════════════════════════════════════
Technical Score (API + MCP):     75/100
Sentiment Boost (WebFetch):      +10
Pattern History (MCP Memory):    +8
Lunar Phase Modifier:            +5
─────────────────────────────────────────────────────────
FINAL CONFIDENCE:                98/100 ✅

💡 DECISION: BUY BTC
  ├─ Entry: $43,850
  ├─ Size: $18 (30% of capital - high confidence)
  ├─ Stop: $42,755 (-2.5%)
  ├─ Target 1: $45,167 (+3%)
  ├─ Target 2: $46,043 (+5%)
  └─ Risk/Reward: 2.1:1
╚════════════════════════════════════════════════════════════╝
```

---

## Summary

**API** (Coinbase) = Trading execution & real-time prices
**WebFetch** = Market sentiment, news, public intelligence
**MCP** = Calculations, memory, reusable tools

**All three work together for research-sound, validated trade decisions.**

Ready to build this architecture?
