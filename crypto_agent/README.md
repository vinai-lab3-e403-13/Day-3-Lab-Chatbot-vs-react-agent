# Crypto Investment ReAct Agent

A complete ReAct agent implementation for crypto investment assistance, built as a separate module to compare against the baseline `src/agent/agent.py`.

## Architecture

```
crypto_agent/
├── agent.py           # CryptoReActAgent (complete ReAct implementation)
├── chat.py            # Interactive CLI chat interface
├── gui.py            # Streamlit GUI with visualizations
├── tools/             # Crypto investment tools
│   ├── price_tool.py      # get_crypto_price
│   ├── portfolio_tool.py  # get_portfolio
│   └── calculator_tool.py # calculate_investment
└── trace_generator.py # Generates evaluation traces
```

## Tools

### get_crypto_price
Returns current USD price and 24h change for a cryptocurrency.

```
Input:  crypto_id (e.g., 'bitcoin', 'ethereum', 'solana', 'cardano')
Output: {"crypto": "bitcoin", "price_usd": 67500.0, "change_24h": 2.35}
```

### get_portfolio
Returns user's mock portfolio holdings.

```
Input:  user_id (optional, defaults to 'default')
Output: {"total_value_usd": 10500.0, "holdings": [{"crypto": "bitcoin", "amount": 0.15, "value_usd": 6000.0}, ...]}
```

### calculate_investment
Calculates crypto amount from USD and optional profit projection.

```
Input:  amount_usd (float), crypto_id (str), expected_gain_pct (float, optional)
Output: {"investment_usd": 1000, "crypto_id": "ethereum", "amount_crypto": 0.357, "current_price": 2800, "expected_gain_pct": 10, "final_value_usd": 1100, "profit_usd": 100}
```

## Usage

### Streamlit GUI (Recommended)

Launch a visual interface with chain-of-thoughts visualization, token metrics, and session statistics.

```bash
# Trên macOS/Linux
.venv/bin/pip install streamlit pandas
.venv/bin/streamlit run crypto_agent/gui.py --server.port 8501

# Trên Windows
.\.venv\Scripts\pip install streamlit pandas
.\.venv\Scripts\streamlit run crypto_agent\gui.py --server.port 8501
```

Features:
- **Chat Interface**: Interactive chat with the agent
- **Chain of Thoughts**: Visual display of Thought → Action → Observation → Final Answer
- **Token Metrics**: Per-request and cumulative token usage
- **Latency Tracking**: Response time for each request
- **Tools Used**: Bar chart of which tools are called most
- **Session Statistics**: Table and line charts of all sessions

### Interactive CLI Chat

```bash
.venv/bin/python crypto_agent/chat.py
```

Commands:
- `quit` / `exit` - End session
- `trace` - Show last execution trace
- `provider <name>` - Switch provider (openai/google/local)

### Generate Test Traces

```bash
.venv/bin/python crypto_agent/trace_generator.py
```

Outputs to `traces/` directory as JSON files.

## ReAct Loop Implementation

The `CryptoReActAgent` follows the Thought-Action-Observation cycle:

1. **Thought**: Agent reasons about what to do
2. **Action**: Agent calls a tool with arguments
3. **Observation**: Tool result is fed back into the prompt
4. Repeat until `Final Answer`

Key methods in `agent.py`:
- `get_system_prompt()` - Builds prompt with tools + ReAct format + scope restriction
- `run(user_input)` - Executes full ReAct loop, returns `{answer, trace, tokens_used, latency_ms}`
- `_parse_response()` - Extracts Thought/Action/Final Answer via regex
- `_log_chain_step()` - Logs each step to `logs/chain_of_thoughts_YYYY-MM-DD.json`

## Chain of Thoughts Logging

All interactions are logged to `logs/chain_of_thoughts_YYYY-MM-DD.json`:

```json
{"timestamp": "2026-04-06T10:30:00.000Z", "session_id": "a1b2c3d4", "event_type": "USER_INPUT", "user_input": "What's Bitcoin price?"}
{"timestamp": "2026-04-06T10:30:01.000Z", "session_id": "a1b2c3d4", "event_type": "LLM_OUTPUT", "step": 1, "llm_raw_output": "...", "tokens": {...}}
{"timestamp": "2026-04-06T10:30:02.000Z", "session_id": "a1b2c3d4", "event_type": "CHAIN_OF_THOUGHT", "step": 1, "thought": "User wants Bitcoin price..."}
{"timestamp": "2026-04-06T10:30:03.000Z", "session_id": "a1b2c3d4", "event_type": "ACTION", "step": 1, "action": "get_crypto_price", "action_args": {"crypto_id": "bitcoin"}, "observation": "{\"price_usd\": 67500}"}
{"timestamp": "2026-04-06T10:30:04.000Z", "session_id": "a1b2c3d4", "event_type": "FINAL_ANSWER", "step": 2, "final_answer": "Bitcoin is $67,500..."}
```

Event types:
- `USER_INPUT` - User's query
- `LLM_OUTPUT` - Raw LLM response
- `CHAIN_OF_THOUGHT` - Parsed thought reasoning
- `ACTION` - Tool call with arguments and observation
- `FINAL_ANSWER` - Final response to user

## Scope Restriction

The agent is restricted to crypto-related topics. For non-crypto questions:

```
Final Answer: I'm a Crypto Investment Assistant and can only help with cryptocurrency-related questions such as prices, portfolios, and investment calculations.
```

## Trace Structure

Each test case generates a trace with:

```json
{
  "test_case_id": "test_case_1",
  "name": "Check Bitcoin Price",
  "input": "What's the current price of Bitcoin?",
  "expected_success": true,
  "actual_steps": 2,
  "final_answer": "The current price of Bitcoin is $67,500.00...",
  "tokens_used": 596,
  "latency_ms": 3763,
  "full_trace": {
    "input": "...",
    "steps": [
      {
        "step": 1,
        "thought": "I need to retrieve...",
        "action": "get_crypto_price",
        "action_args": {"crypto_id": "bitcoin"},
        "observation": "{\"crypto\": \"bitcoin\", ...}"
      }
    ],
    "total_steps": 2,
    "latency_ms": 3763
  }
}
```

## Comparison with Baseline Agent

| Feature | Baseline (`src/agent/agent.py`) | Crypto (`crypto_agent/agent.py`) |
|---------|--------------------------------|--------------------------------|
| Status | Skeleton with TODOs | Fully implemented |
| Tools | None | 3 crypto tools |
| Parsing | None | Regex-based Thought/Action extraction |
| Telemetry | Logger + metrics | Full trace generation + Chain-of-Thoughts JSON |
| Chat Interface | None | CLI + Streamlit GUI |
| Scope Restriction | None | Non-crypto topics rejected |
