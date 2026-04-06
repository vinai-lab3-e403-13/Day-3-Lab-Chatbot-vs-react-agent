"""Crypto Investment ReAct Agent - Complete implementation."""

import re
import json
import time
import os
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker
from crypto_agent.tools import get_all_tools, execute_tool


class CryptoReActAgent:
    """
    ReAct Agent specialized for crypto investment assistance.
    Follows Thought-Action-Observation loop with crypto-specific tools.
    """

    def __init__(self, llm: LLMProvider, tools: Optional[List[Dict[str, Any]]] = None, max_steps: int = 10):
        self.llm = llm
        self.tools = tools if tools is not None else get_all_tools()
        self.max_steps = max_steps
        self.history = []
        self._setup_chain_logger()

    def _setup_chain_logger(self):
        """Setup logger for detailed chain of thoughts."""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        chain_log_file = os.path.join(log_dir, f"chain_of_thoughts_{datetime.now().strftime('%Y-%m-%d')}.json")
        self._chain_logger = logging.getLogger("crypto_agent_chain")
        self._chain_logger.setLevel(logging.INFO)
        handler = logging.FileHandler(chain_log_file)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self._chain_logger.addHandler(handler)

    def _log_chain_step(self, session_id: str, step_data: Dict[str, Any]):
        """Log a single chain of thoughts step to JSON file."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            **step_data
        }
        self._chain_logger.info(json.dumps(entry))

    def get_system_prompt(self) -> str:
        """Build system prompt with crypto tools and ReAct format."""
        tool_descriptions = "\n".join([
            f"- {t['name']}: {t['description']}" for t in self.tools
        ])
        return f"""You are a Crypto Investment Assistant. You help users with:
- Checking current cryptocurrency prices and short-term price moves
- Reviewing the available demo portfolio
- Calculating investment scenarios and potential returns
- Looking up detailed market data for a coin
- Finding historical prices on specific dates
- Summarizing trending coins, top movers, and global market conditions


Available tools:
{tool_descriptions}

Tool selection rules:
- Use search_crypto when the user gives an ambiguous coin name or ticker and another tool requires a CoinGecko crypto_id.
- Use get_crypto_price for simple current price checks.
- Use get_crypto_price_cmc when the user asks for richer quote data such as market cap, volume, or 1h or 7d changes.
- Use get_market_data for broader coin market statistics such as rank, all-time high, supply, and 24h high or low.
- Use get_historical_price for price questions tied to a specific date.
- Use get_top_movers, get_trending_coins, and get_global_market_data for market-overview questions.
- Use get_portfolio only for the available demo portfolio data.
- If a tool returns an error, use that error to choose a better next step or explain the limitation clearly.

Follow this format exactly:
Thought: brief reasoning about what to do next
Action: tool_name({{"arg1": "value1"}})
Observation: result of tool call
... (repeat if needed)
Final Answer: concise response to the user

Rules:
- Use at most one Action per response.
- Action arguments must be valid JSON using double quotes.
- Do not wrap the response in code fences.
- Do not invent observations.
- If no tool is needed, respond directly with Final Answer."""

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse Thought, Action, and Final Answer from LLM response."""
        result = {
            "thought": None,
            "action": None,
            "action_args": None,
            "final_answer": None
        }

        thought_match = re.search(r"Thought:\s*(.+?)(?=\nAction:|\nFinal Answer:|$)", content, re.DOTALL)
        if thought_match:
            result["thought"] = thought_match.group(1).strip()

        action_match = re.search(r"Action:\s*(\w+)\s*\(\s*(\{[^}]*\})\s*\)", content)
        if action_match:
            result["action"] = action_match.group(1)
            args_str = action_match.group(2)
            try:
                result["action_args"] = json.loads(args_str)
            except json.JSONDecodeError:
                result["action_args"] = {"raw": args_str}

        final_match = re.search(r"Final Answer:\s*(.+)", content, re.DOTALL)
        if final_match:
            result["final_answer"] = final_match.group(1).strip()

        return result

    def _build_prompt(self, user_input: str, steps_data: List[Dict[str, Any]]) -> str:
        """Build the prompt including history of steps."""
        prompt = user_input
        for step in steps_data:
            prompt += f"\n\nThought: {step['thought']}"
            if step.get('action'):
                args_str = json.dumps(step['action_args']) if step['action_args'] else "{}"
                prompt += f"\nAction: {step['action']}({args_str})"
            if step.get('observation'):
                prompt += f"\nObservation: {step['observation']}"
        return prompt

    def run(self, user_input: str) -> Dict[str, Any]:
        """
        Execute the ReAct loop and return result with trace.

        Returns:
            Dict with 'answer', 'trace', 'tokens_used', 'latency_ms'
        """
        session_id = str(uuid.uuid4())[:8]

        trace = {
            "input": user_input,
            "steps": [],
            "model": self.llm.model_name,
            "session_id": session_id
        }

        start_time = time.time()
        logger.log_event("CRYPTO_AGENT_START", {"input": user_input, "model": self.llm.model_name})

        # Log user input to chain of thoughts
        self._log_chain_step(session_id, {
            "event_type": "USER_INPUT",
            "user_input": user_input
        })

        steps_data = []
        current_prompt = user_input
        steps = 0
        final_answer = None

        while steps < self.max_steps:
            response = self.llm.generate(
                current_prompt,
                system_prompt=self.get_system_prompt()
            )

            content = response["content"]
            parsed = self._parse_response(content)

            step_record = {
                "step": steps + 1,
                "llm_output": content,
                "tokens": response["usage"]
            }

            # Log LLM raw output to chain of thoughts
            self._log_chain_step(session_id, {
                "event_type": "LLM_OUTPUT",
                "step": steps + 1,
                "llm_raw_output": content,
                "tokens": response["usage"]
            })

            if parsed["thought"]:
                step_record["thought"] = parsed["thought"]
                # Log chain of thought
                self._log_chain_step(session_id, {
                    "event_type": "CHAIN_OF_THOUGHT",
                    "step": steps + 1,
                    "thought": parsed["thought"]
                })

            if parsed["action"]:
                tool_name = parsed["action"]
                args = parsed["action_args"] or {}
                observation = execute_tool(tool_name, **args)

                step_record["action"] = tool_name
                step_record["action_args"] = args
                step_record["observation"] = observation

                steps_data.append({
                    "thought": parsed["thought"],
                    "action": tool_name,
                    "action_args": args,
                    "observation": observation
                })

                # Log action
                self._log_chain_step(session_id, {
                    "event_type": "ACTION",
                    "step": steps + 1,
                    "action": tool_name,
                    "action_args": args,
                    "observation": observation
                })

                current_prompt = self._build_prompt(user_input, steps_data)
                # Always loop back so the LLM sees the REAL observation
                # before producing a final answer — ignore any hallucinated
                # final answer bundled in the same response as an action.
                trace["steps"].append(step_record)
                tracker.track_request(
                    provider=response["provider"],
                    model=self.llm.model_name,
                    usage=response["usage"],
                    latency_ms=response["latency_ms"]
                )
                steps += 1
                continue
            else:
                steps_data.append({
                    "thought": parsed["thought"] or "No action needed"
                })

            if parsed["final_answer"]:
                final_answer = parsed["final_answer"]
                step_record["final_answer"] = final_answer
                # Log final answer
                self._log_chain_step(session_id, {
                    "event_type": "FINAL_ANSWER",
                    "step": steps + 1,
                    "final_answer": final_answer
                })

            trace["steps"].append(step_record)

            tracker.track_request(
                provider=response["provider"],
                model=self.llm.model_name,
                usage=response["usage"],
                latency_ms=response["latency_ms"]
            )

            if final_answer:
                break

            steps += 1

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        trace["total_steps"] = steps + 1
        trace["latency_ms"] = latency_ms
        trace["final_answer"] = final_answer or "Agent did not produce final answer"

        self.history = steps_data

        logger.log_event("CRYPTO_AGENT_END", trace)

        return {
            "answer": final_answer or "Max steps exceeded",
            "trace": trace,
            "tokens_used": sum(s["tokens"]["total_tokens"] for s in trace["steps"]),
            "latency_ms": latency_ms
        }
