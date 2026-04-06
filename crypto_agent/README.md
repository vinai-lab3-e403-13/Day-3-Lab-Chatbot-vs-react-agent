# Crypto Investment ReAct Agent

A complete ReAct agent implementation for crypto investment assistance, built as a separate module to compare against the baseline `src/agent/agent.py`.

## Architecture

```
crypto_agent/
├── agent.py           # CryptoReActAgent (complete ReAct implementation)
├── chat.py            # Interactive CLI chat interface
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

### Interactive Chat

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
- `get_system_prompt()` - Builds prompt with tools + ReAct format
- `run(user_input)` - Executes full ReAct loop, returns `{answer, trace, tokens_used, latency_ms}`
- `_parse_response()` - Extracts Thought/Action/Final Answer via regex
- `_execute_tool()` - Dispatches to tool functions

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
| Telemetry | Logger + metrics | Full trace generation |
| Chat Interface | None | Interactive CLI |
