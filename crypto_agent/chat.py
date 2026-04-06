"""Interactive CLI chat interface for Crypto Agent."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from crypto_agent.agent import CryptoReActAgent
from crypto_agent.tools import get_all_tools
from src.core.llm_provider import LLMProvider


def create_provider(provider_type: str = None) -> LLMProvider:
    """Factory function to create LLM provider."""
    load_dotenv()

    if provider_type is None:
        provider_type = os.getenv("DEFAULT_PROVIDER", "openai")

    if provider_type == "openai":
        from src.core.openai_provider import OpenAIProvider
        return OpenAIProvider(
            model_name=os.getenv("DEFAULT_MODEL", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
    elif provider_type == "google":
        from src.core.gemini_provider import GeminiProvider
        return GeminiProvider(
            model_name="gemini-1.5-flash",
            api_key=os.getenv("GEMINI_API_KEY")
        )
    elif provider_type == "local":
        from src.core.local_provider import LocalProvider
        return LocalProvider(
            model_path=os.getenv("LOCAL_MODEL_PATH")
        )
    else:
        raise ValueError(f"Unknown provider: {provider_type}")


def main():
    print("=" * 60)
    print("  Crypto Investment Assistant - Interactive CLI")
    print("=" * 60)
    print("\nAvailable commands:")
    print("  - Type your crypto question or request")
    print("  - 'quit' or 'exit' to end session")
    print("  - 'trace' to show last execution trace")
    print("  - 'provider <name>' to switch provider (openai/google/local)")
    print()

    provider = create_provider()
    tools = get_all_tools()
    agent = CryptoReActAgent(provider, tools, max_steps=5)

    last_trace = None
    last_result = None

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye!")
                break

            if user_input.lower() == "trace":
                if last_trace:
                    print("\n" + "=" * 40)
                    print("LAST EXECUTION TRACE")
                    print("=" * 40)
                    for step in last_trace["steps"]:
                        print(f"\nStep {step['step']}:")
                        if step.get("thought"):
                            print(f"  Thought: {step['thought'][:100]}...")
                        if step.get("action"):
                            print(f"  Action: {step['action']}({step.get('action_args', {})})")
                        if step.get("observation"):
                            print(f"  Observation: {step['observation'][:100]}...")
                        if step.get("final_answer"):
                            print(f"  Final Answer: {step['final_answer'][:100]}...")
                else:
                    print("No trace available yet.")
                continue

            if user_input.lower().startswith("provider "):
                new_provider = user_input.split(" ", 1)[1].strip()
                try:
                    provider = create_provider(new_provider)
                    agent = CryptoReActAgent(provider, tools, max_steps=5)
                    print(f"Switched to {new_provider} provider.\n")
                except Exception as e:
                    print(f"Failed to switch provider: {e}\n")
                continue

            if not user_input:
                continue

            print("\nAssistant: ", end="", flush=True)
            result = agent.run(user_input)

            print(result["answer"])
            print(f"\n[Metrics: {result['tokens_used']} tokens, {result['latency_ms']}ms, {len(result['trace']['steps'])} steps]\n")

            last_trace = result["trace"]
            last_result = result

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
