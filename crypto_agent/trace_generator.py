"""Generate evaluation traces for 5 test cases."""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_agent.agent import CryptoReActAgent
from crypto_agent.tools import get_all_tools
from src.core.openai_provider import OpenAIProvider


def generate_traces():
    """Generate 5 test case traces and save to traces/ directory."""
    os.makedirs("traces", exist_ok=True)

    load_dotenv()
    provider = OpenAIProvider()
    tools = get_all_tools()
    agent = CryptoReActAgent(provider, tools, max_steps=5)

    test_cases = [
        {
            "id": "test_case_1",
            "name": "Check Bitcoin Price",
            "input": "What's the current price of Bitcoin?",
            "expected_tools": ["get_crypto_price"],
            "expected_success": True
        },
        {
            "id": "test_case_2",
            "name": "Portfolio Review",
            "input": "Show me my portfolio balance",
            "expected_tools": ["get_portfolio"],
            "expected_success": True
        },
        {
            "id": "test_case_3",
            "name": "Investment Calculation",
            "input": "If I invest $1000 in Ethereum with 10% gain, what would I get?",
            "expected_tools": ["calculate_investment"],
            "expected_success": True
        },
        {
            "id": "test_case_4",
            "name": "Multi-Step Analysis",
            "input": "What's my portfolio value and how much Bitcoin do I own?",
            "expected_tools": ["get_portfolio"],
            "expected_success": True
        },
        {
            "id": "test_case_5",
            "name": "Unknown Crypto Handling",
            "input": "What's the price of nonexistentcoin12345?",
            "expected_tools": ["get_crypto_price"],
            "expected_success": False
        }
    ]

    print("=" * 60)
    print("  Crypto Agent - Trace Generator")
    print("=" * 60)
    print(f"\nGenerating {len(test_cases)} test case traces...\n")

    for tc in test_cases:
        print(f"Running {tc['id']}: {tc['name']}...")
        try:
            result = agent.run(tc["input"])

            trace = {
                "test_case_id": tc["id"],
                "name": tc["name"],
                "timestamp": datetime.utcnow().isoformat(),
                "input": tc["input"],
                "expected_success": tc["expected_success"],
                "expected_tools": tc["expected_tools"],
                "actual_steps": len(result["trace"]["steps"]),
                "final_answer": result["answer"],
                "tokens_used": result["tokens_used"],
                "latency_ms": result["latency_ms"],
                "full_trace": result["trace"]
            }

            status = "success" if tc["expected_success"] else "failed"
            filename = f"traces/{tc['id']}_{status}.json"
            with open(filename, "w") as f:
                json.dump(trace, f, indent=2)

            print(f"  - Steps: {len(result['trace']['steps'])}")
            print(f"  - Tokens: {result['tokens_used']}")
            print(f"  - Saved: {filename}\n")

        except Exception as e:
            print(f"  - ERROR: {e}\n")

    print("=" * 60)
    print("  Trace generation complete!")
    print("  Traces saved to: traces/")
    print("=" * 60)


if __name__ == "__main__":
    generate_traces()
