# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: E403-13
- **Team Members**: Trần Kiên Trường (tktrev), Đặng Thanh Tùng (dangth), Trịnh Ngọc Tú (cheeka13), Long
- **Deployment Date**: 06-04-2026

---

## 1. Executive Summary

The Crypto Investment ReAct Agent is a production-grade AI agent that helps users with cryptocurrency investment queries through a Thought-Action-Observation loop. The agent integrates with real APIs (CoinGecko, CoinMarketCap) to provide live prices, portfolio analysis, market data, and investment calculations.

- **Success Rate**: 80% (4 of 5 test cases passed)
- **Key Outcome**: The ReAct agent solved 100% of multi-step queries (portfolio review + Bitcoin ownership) where a baseline chatbot would hallucinate. The chain-of-thoughts logging enabled rapid debugging of hallucinated tool calls.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation

```
User Input → Build Prompt (System + History)
    ↓
LLM.generate() → Parse Response (Thought/Action/Final Answer)
    ↓
If Action → Execute Tool → Build Observation → Append to Prompt → Loop
If Final Answer → Return Result + Trace
```

Key files:
- `crypto_agent/agent.py` - Core CryptoReActAgent with chain-of-thoughts logging
- `crypto_agent/tools/` - 10 crypto investment tools
- `crypto_agent/gui.py` - Streamlit visualization GUI
- `src/telemetry/` - IndustryLogger + PerformanceTracker

### 2.2 Tool Definitions (Inventory)

| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `get_crypto_price` | `{"crypto_id": "bitcoin"}` | Simple price + 24h change via CoinGecko |
| `get_crypto_price_cmc` | `{"crypto_id": "bitcoin"}` | Rich quote (market cap, volume, 1h/7d changes) via CoinMarketCap |
| `get_market_data` | `{"crypto_id": "bitcoin"}` | Detailed market stats (rank, ATH, supply, high/low) |
| `get_historical_price` | `{"crypto_id": "ethereum", "date": "01-01-2020"}` | Historical price on specific date |
| `get_portfolio` | `{"user_id": "default"}` | Demo portfolio holdings and total value |
| `calculate_investment` | `{"amount_usd": 1000, "crypto_id": "ethereum", "expected_gain_pct": 10}` | Investment profit projection |
| `get_top_movers` | `{"limit": 5}` | Top gainers/losers by 24h change |
| `get_trending_coins` | `{}` | Top 7 trending coins on CoinGecko |
| `get_global_market_data` | `{}` | Global market cap, volume, BTC dominance |
| `search_crypto` | `{"query": "bnb"}` | Find CoinGecko ID by name/symbol |

### 2.3 LLM Providers Used

- **Primary**: GPT-4o (OpenAI)
- **Secondary (Backup)**: Gemini 1.5 Flash (Google)
- **Local Development**: Phi-3-mini-4k-instruct-q4.gguf via llama-cpp-python

---

## 3. Telemetry & Performance Dashboard

*Based on 5 official test traces and runtime logs.*

- **Average Latency (P50)**: ~2,349ms per task
- **Max Latency (P99)**: ~3,763ms (Bitcoin price check - 2 steps)
- **Average Tokens per Task**: ~473 tokens
- **Total Cost of Test Suite**: ~$0.024 (at $0.01/1K tokens)

**Per-Trace Breakdown:**

| Test Case | Steps | Latency | Tokens | Status |
| :--- | :--- | :--- | :--- | :--- |
| Bitcoin Price | 2 | 3,763ms | 596 | ✅ Pass |
| Portfolio Review | 1 | 2,017ms | 354 | ✅ Pass |
| Investment Calc | 1 | 2,323ms | 406 | ✅ Pass |
| Multi-Step Portfolio | 2 | 1,529ms | 685 | ✅ Pass |
| Unknown Crypto | 1 | 2,114ms | 327 | ⚠️ Expected Fail |

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study: Hallucinated Tool Name (`get_crypto_price_cmc`)

- **Input**: "What is bitcoin price based from coinmarketcap"
- **Observation**: Agent called `get_crypto_price_cmc` which returned error `{"error": "Tool 'get_crypto_price_cmc' not found"}`, but then hallucinated a final answer: "The current price of Bitcoin on CoinMarketCap is $34,357.23"
- **Root Cause**: The tool DID exist in `tools/__init__.py` but was not registered in the `tool_map` in `execute_tool()`, so the agent received an error despite the tool definition being present in the system prompt
- **Evidence**: `logs/chain_of_thoughts_2026-04-06.json` lines 25-28

**Fix Applied**: Re-registered `get_crypto_price_cmc` in the tool execution map. Additionally, added explicit tool selection rules to the system prompt:
```
- Use get_crypto_price for simple current price checks.
- Use get_crypto_price_cmc when the user asks for richer quote data such as market cap, volume, or 1h or 7d changes.
```

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 (scope restriction) vs Prompt v2 (scope + tool selection rules)

- **v1**: Basic scope restriction ("Only answer crypto questions")
- **v2**: Added explicit tool selection rules and error handling guidance

**Result**: v2 reduced hallucinated tool calls from ~15% to ~5% on market cap queries.

### Experiment 2: Chatbot vs Agent

| Case | Chatbot Behavior | Agent Behavior | Winner |
| :--- | :--- | :--- | :--- |
| "What's Bitcoin price?" | Direct answer (may hallucinate) | Calls `get_crypto_price` → Real data | **Agent** |
| "My portfolio value?" | Hallucinates values | Calls `get_portfolio` → Real data | **Agent** |
| "What's ETH price + my BTC?" | Single answer only | 2-step reasoning | **Agent** |
| Non-crypto query | May answer incorrectly | Rejects with scope message | **Agent** |
| Unknown crypto | Hallucinates price | Graceful error | **Agent** |

---

## 6. Production Readiness Review

- **Security**: Input sanitization is needed for tool arguments (e.g., crypto_id should be validated against allowlist). API keys stored in environment variables.
- **Guardrails**: Implemented max 10 steps to prevent infinite loops. Non-crypto queries are explicitly rejected with a scope message.
- **Scaling**: For 50+ tools, consider vector DB retrieval for semantic tool selection. For concurrent requests, an async queue with `asyncio` would help.
- **Error Recovery**: When a tool fails (API timeout, rate limit), the agent should retry with exponential backoff or fallback to an alternative data source.
- **Observability**: Chain-of-thoughts logging to `logs/chain_of_thoughts_YYYY-MM-DD.json` provides full audit trail for post-hoc debugging.

---

> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in this folder.
