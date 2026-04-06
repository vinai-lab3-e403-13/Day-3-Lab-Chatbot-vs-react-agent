# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Trần Kiên Trường
- **Student ID**: 2A202600496
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

- **Modules Implemented**:
  - `crypto_agent/agent.py` - Core CryptoReActAgent implementation with Thought-Action-Observation loop
  - `crypto_agent/chat.py` - Interactive CLI chat interface
  - `crypto_agent/gui.py` - Streamlit GUI with chain-of-thoughts visualization
  - `crypto_agent/trace_generator.py` - Test trace generation
  - `crypto_agent/tools/` - Crypto investment tools (price, portfolio, calculator)
  - `flowchart.md` - System architecture documentation

- **Code Highlights**:

  **Chain of Thoughts Logging** (`crypto_agent/agent.py:34-53`):
  ```python
  def _setup_chain_logger(self):
      """Setup logger for detailed chain of thoughts."""
      chain_log_file = os.path.join(log_dir, f"chain_of_thoughts_{datetime.now().strftime('%Y-%m-%d')}.json")
      self._chain_logger = logging.getLogger("crypto_agent_chain")

  def _log_chain_step(self, session_id: str, step_data: Dict[str, Any]):
      """Log a single chain of thoughts step to JSON file."""
      entry = {
          "timestamp": datetime.utcnow().isoformat(),
          "session_id": session_id,
          **step_data
      }
      self._chain_logger.info(json.dumps(entry))
  ```

  **GUI Session Tracking** (`crypto_agent/gui.py:1-329`):
  - Full Streamlit interface with chat, token metrics, and visualization

- **Documentation**: The chain of thoughts logging logs each ReAct step to `logs/chain_of_thoughts_YYYY-MM-DD.json` with event types: `USER_INPUT`, `LLM_OUTPUT`, `CHAIN_OF_THOUGHT`, `ACTION`, and `FINAL_ANSWER`. This enables post-hoc debugging and performance analysis.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: The LLM was hallucinating a non-existent tool `get_crypto_price_cmc` when users asked for market cap data. When executed, the tool returned an error: `{"error": "Tool 'get_crypto_price_cmc' not found"}`, but the agent still produced a hallucinated final answer instead of acknowledging the error.

- **Log Source**: `logs/chain_of_thoughts_2026-04-06.json`
  ```json
  {"timestamp": "2026-04-06T09:42:26.048198", "session_id": "e2da96d6", "event_type": "ACTION", "step": 1, "action": "get_crypto_price_cmc", "action_args": {"crypto_id": "bitcoin"}, "observation": "{\"error\": \"Tool 'get_crypto_price_cmc' not found\"}"}
  {"timestamp": "2026-04-06T09:42:26.048261", "session_id": "e2da96d6", "event_type": "FINAL_ANSWER", "step": 1, "final_answer": "The current price of Bitcoin on CoinMarketCap is $34,357.23."}
  ```

- **Diagnosis**: The issue was twofold:
  1. The system prompt lacked explicit tool selection rules for market cap queries
  2. When the tool failed, the agent had no error-handling logic to retry with a correct tool

- **Solution**: Updated the system prompt with explicit tool selection rules:
  ```
  - Use get_crypto_price for simple current price checks.
  - Use get_crypto_price_cmc when the user asks for richer quote data such as market cap, volume, or 1h or 7d changes.
  - Use get_market_data for broader coin market statistics such as rank, all-time high, supply, and 24h high or low.
  ```

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: The `Thought` block forces the LLM to externalize its reasoning before taking action. Unlike a chatbot that jumps directly to an answer, the ReAct agent must articulate "why" it is calling a particular tool. This dramatically reduces hallucination because we can see the chain of thought before the action. For example, if the thought says "use get_crypto_price_cmc for market cap" but the tool doesn't exist, the error is caught.

2. **Reliability**: The ReAct agent performed worse in:
   - **Simple queries**: For trivial questions like "hi" or "what's 2+2", the ReAct loop adds unnecessary latency and complexity
   - **Non-crypto queries**: Without scope restriction, the agent would try to use tools for topics outside its domain
   - **Ambiguous queries**: When a user says "What's Bitcoin price based from coinmarketcap", the agent might hallucinate a tool name instead of using the available `get_crypto_price`

3. **Observation**: The observation feedback is critical - it's what makes the loop "reactive." Each observation becomes context for the next iteration. When `get_crypto_price` returns `{"price_usd": 67500.0}`, the next thought can reason about this specific value rather than making up a number. Without real observations, the agent is just a sophisticated autocomplete.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Implement an asynchronous tool execution queue using `asyncio` with concurrent tool calls. When the agent needs data from multiple independent sources (e.g., Bitcoin price + Ethereum price), they can be fetched in parallel rather than sequentially.

- **Safety**: Add a "Supervisor" LLM that audits each action before execution. The supervisor would validate that: (1) the tool exists, (2) the arguments are valid, (3) the action aligns with user intent. This prevents hallucinated tool calls like `get_crypto_price_cmc`.

- **Performance**: For systems with many tools (50+), use vector embeddings of tool descriptions for semantic retrieval. Instead of passing all tools in the prompt, retrieve the top-k relevant tools based on the user's query - this reduces token cost and improves accuracy.

- **Error Recovery**: Implement automatic retry with fallback: when a tool fails, the agent should try an alternative tool (e.g., fallback from CoinGecko to CoinMarketCap) rather than producing a hallucinated answer.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
