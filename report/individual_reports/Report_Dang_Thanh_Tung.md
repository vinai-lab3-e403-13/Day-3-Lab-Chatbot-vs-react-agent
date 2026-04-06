# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Dang Thanh Tung
- **Student ID**: 2A202600023
- **Date**: 2026/4/6

---

## I. Technical Contribution (15 Points)

- I implemented `coinmarketcap_tool.py` and test it
- I updated the system prompt follow new tools set
- I fixed bug: if at a step, the prompt result return both `Action` and `Final Result`, it still call the action but then ignore the action result and return the outdated `Final Result` (instead needs to loop more)
- I updated behavior: when max_steps reached, it tried to return the latest `Final Result` from **trace**, instead of just an error "Max steps reached"

- **Modules Implementated**: 
  - `crypto_agent/tools/coinmarketcap_tool.py`
  - `tests/test_coinmarketcap_tool.py`
- **Code Highlights**:
```py
# coinmarketcap_tool.py
# only support certain symbols
def get_crypto_price_cmc(crypto_id: str, api_key: Optional[str] = None) -> str:
    # ...
    # Resolve alias (e.g., "bitcoin" -> "BTC")
    symbol = SYMBOL_ALIASES.get(crypto_id.lower(), crypto_id.upper())

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": key,
    }
    params = {
        "symbol": symbol,
        "convert": "USD",
    }

    try:
        response = requests.get(
            f"{CMC_BASE_URL}/cryptocurrency/quotes/latest",
            headers=headers,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        #...validate result
        coin_data = data.get("data", {}).get(symbol)
        quote = coin_data["quote"]["USD"]

        return json.dumps({
            "crypto": coin_data["name"],
            "symbol": coin_data["symbol"],
            "price_usd": round(quote["price"], 6),
            "market_cap_usd": round(quote["market_cap"], 2),
            "volume_24h_usd": round(quote["volume_24h"], 2),
            "change_1h": round(quote["percent_change_1h"], 2),
            "change_24h": round(quote["percent_change_24h"], 2),
            "change_7d": round(quote["percent_change_7d"], 2),
            "last_updated": quote["last_updated"],
        })

    except requests.exceptions.Timeout:
    #...more exception, dump json_error

# test_coinmarketcap_tool.py
def run_test(label: str, crypto_id: str):
def test_missing_api_key():
def test_invalid_symbol():

if __name__ == "__main__":
    run_test("Full name  → bitcoin",   "bitcoin")
    run_test("Full name  → ethereum",  "ethereum")
    run_test("Full name  → solana",    "solana")
    run_test("Ticker sym → BTC",       "BTC")
    run_test("Ticker sym → ETH",       "ETH")
    run_test("Ticker sym → SOL",       "SOL")

    # --- Edge-case tests ---
    test_missing_api_key()
    test_invalid_symbol()
```

- **Documentation**: [Brief explanation of how your code interacts with the ReAct loop]

---

## II. Debugging Case Study (10 Points)

**Ignore Action call observation**

- **Problem Description**: When using old system prompt, at a step it returns both Action, and FinalResult => leads to ignore the Action and return uncompleted FinalResult immediately
- **Log Source**: (I dont have right now)
- **Diagnosis**: I think it was the system prompt, it return the Action need to call and the fake FinalResult at the same step.
- **Solution**: If there is an Action, ignore FinalResult at that step and move on to the next step

**Return nothing at max steps**

- **Problem Description**: when reach max_steps it return a simple text "Max steps reached" ignoring all the results before it.
```json
{"timestamp": "2026-04-06T14:25:16.471167", "session_id": "32a314de", "event_type": "USER_INPUT", "user_input": "get eth price in 2026 jan 1 using historical price tool"}
{"timestamp": "2026-04-06T14:25:18.216381", "session_id": "32a314de", "event_type": "LLM_OUTPUT", "step": 1, "llm_raw_output": "The historical price tool can't predict future prices; it only provides past data. If you're interested in a future price scenario, we can discuss potential investment calculations or consult market experts for forecasts. Let me know if you'd like to explore those options!", "tokens": {"prompt_tokens": 849, "completion_tokens": 48, "total_tokens": 897}}
{"timestamp": "2026-04-06T14:25:20.006002", "session_id": "32a314de", "event_type": "LLM_OUTPUT", "step": 2, "llm_raw_output": "I'm unable to retrieve future prices with the historical price tool, as it only provides past data. If you need help with other types of price analysis or projections within the available datasets, please let me know!", "tokens": {"prompt_tokens": 849, "completion_tokens": 41, "total_tokens": 890}}
{"timestamp": "2026-04-06T14:25:22.027377", "session_id": "32a314de", "event_type": "LLM_OUTPUT", "step": 3, "llm_raw_output": "The get_historical_price tool can only retrieve past prices, not future ones. Therefore, I cannot provide the price of Ethereum for a future date like January 1, 2026. If you have any other questions or need assistance with a different tool, feel free to ask!", "tokens": {"prompt_tokens": 849, "completion_tokens": 57, "total_tokens": 906}}
{"timestamp": "2026-04-06T14:25:23.966815", "session_id": "32a314de", "event_type": "LLM_OUTPUT", "step": 4, "llm_raw_output": "The get_historical_price tool can only access historical data and cannot predict future prices. If you have any other type of request or need historical data, feel free to ask!", "tokens": {"prompt_tokens": 849, "completion_tokens": 35, "total_tokens": 884}}
{"timestamp": "2026-04-06T14:25:25.535672", "session_id": "32a314de", "event_type": "LLM_OUTPUT", "step": 5, "llm_raw_output": "The historical price tool can only retrieve past prices, not future predictions. Therefore, I can't provide a price for ETH on January 1, 2026. \n\nFor future price estimates, consider consulting price predictions from financial analysts or market forecasts. Let me know if you need something else!", "tokens": {"prompt_tokens": 849, "completion_tokens": 58, "total_tokens": 907}}
```

- **Solution**: instead of return simple text error, try to get the latest result from **trace**

**Can not get historical price**

About the above logs, when i input `"get eth price in 2026 jan 1 using historical price tool"`, it return error like `"can not get future price"`, repeat 5 times (max steps) and stopped

But when i input `"today is 2026 April, get eth price in 2026 jan 1 using historical price tool"` then it can get the result (perhaps it needs tool to get today info)

```json
{"timestamp": "2026-04-06T14:27:09.799253", "session_id": "c7a39897", "event_type": "USER_INPUT", "user_input": "today is 2026 April, get eth price in 2026 jan 1 using historical price tool"}
{"timestamp": "2026-04-06T14:27:11.487328", "session_id": "c7a39897", "event_type": "LLM_OUTPUT", "step": 1, "llm_raw_output": "Thought: I need to get the historical price of Ethereum on January 1, 2026, using the historical price tool.\nAction: get_historical_price({\"crypto_id\": \"ethereum\", \"date\": \"01-01-2026\"})", "tokens": {"prompt_tokens": 856, "completion_tokens": 50, "total_tokens": 906}}
{"timestamp": "2026-04-06T14:27:11.487614", "session_id": "c7a39897", "event_type": "CHAIN_OF_THOUGHT", "step": 1, "thought": "I need to get the historical price of Ethereum on January 1, 2026, using the historical price tool."}
{"timestamp": "2026-04-06T14:27:11.892346", "session_id": "c7a39897", "event_type": "ACTION", "step": 1, "action": "get_historical_price", "action_args": {"crypto_id": "ethereum", "date": "01-01-2026"}, "observation": "{\"crypto_id\": \"ethereum\", \"date\": \"01-01-2026\", \"price_usd\": 2966.7741798134107}"}
{"timestamp": "2026-04-06T14:27:12.718485", "session_id": "c7a39897", "event_type": "LLM_OUTPUT", "step": 2, "llm_raw_output": "Final Answer: The price of Ethereum on January 1, 2026, was approximately $2,966.77.", "tokens": {"prompt_tokens": 942, "completion_tokens": 25, "total_tokens": 967}}
{"timestamp": "2026-04-06T14:27:12.718609", "session_id": "c7a39897", "event_type": "FINAL_ANSWER", "step": 2, "final_answer": "The price of Ethereum on January 1, 2026, was approximately $2,966.77."}
```

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: The `Thought` block helped the agent break the task into steps, choose the right tool, and avoid answering only from memory like a normal chatbot.
2.  **Reliability**: The Agent performed worse when it chose a wrong assumption and repeated it across many steps, such as treating a valid past date as a future date and looping until max steps.
3.  **Observation**: Observations were useful because tool outputs gave real feedback for the next step, but if the observation was misunderstood, the agent could keep following the wrong path.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Use async tool calls and a queue so the agent can handle more users at the same time.
- **Safety**: Add validation rules and a supervisor check before executing risky or invalid tool actions.
- **Performance**: Cache common results and improve tool selection so the agent uses fewer unnecessary steps.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
