"""Test script for get_crypto_price_cmc function."""

import os
import sys
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_agent.tools.coinmarketcap_tool import get_crypto_price_cmc

load_dotenv()


def run_test(label: str, crypto_id: str):
    print(f"\n{'─' * 50}")
    print(f"🔍 Test: {label}  (input: '{crypto_id}')")
    result = get_crypto_price_cmc(crypto_id)
    data = json.loads(result)

    if "error" in data:
        print(f"  ❌ Error: {data['error']}")
    else:
        print(f"  ✅ {data['crypto']} ({data['symbol']})")
        print(f"     Price      : ${data['price_usd']:,.6f}")
        print(f"     Market Cap : ${data['market_cap_usd']:,.2f}")
        print(f"     Volume 24h : ${data['volume_24h_usd']:,.2f}")
        print(f"     Change  1h : {data['change_1h']:+.2f}%")
        print(f"     Change 24h : {data['change_24h']:+.2f}%")
        print(f"     Change  7d : {data['change_7d']:+.2f}%")
        print(f"     Updated    : {data['last_updated']}")


def test_missing_api_key():
    """Ensure a helpful error is returned when no API key is provided."""
    print(f"\n{'─' * 50}")
    print("🔍 Test: Missing API key")
    result = get_crypto_price_cmc("bitcoin", api_key="")
    data = json.loads(result)
    assert "error" in data, "Expected error when API key is missing"
    print(f"  ✅ Got expected error: {data['error']}")


def test_invalid_symbol():
    """Ensure a helpful error is returned for unknown symbols."""
    print(f"\n{'─' * 50}")
    print("🔍 Test: Invalid / unknown symbol")
    result = get_crypto_price_cmc("NOTACOIN_XYZ")
    data = json.loads(result)
    if "error" in data:
        print(f"  ✅ Got expected error: {data['error']}")
    else:
        print(f"  ⚠️  Unexpected success: {data}")


if __name__ == "__main__":
    print("=" * 50)
    print("  CoinMarketCap Tool — Test Run")
    print("=" * 50)

    api_key = os.environ.get("CMC_API_KEY", "")
    if not api_key:
        print("\n⚠️  CMC_API_KEY not set — live API tests will return an error response.")
    else:
        print(f"\n✅ CMC_API_KEY found (***{api_key[-4:]})")

    # --- Live API tests (require CMC_API_KEY) ---
    run_test("Full name  → bitcoin",   "bitcoin")
    run_test("Full name  → ethereum",  "ethereum")
    run_test("Full name  → solana",    "solana")
    run_test("Ticker sym → BTC",       "BTC")
    run_test("Ticker sym → ETH",       "ETH")
    run_test("Ticker sym → SOL",       "SOL")

    # --- Edge-case tests ---
    test_missing_api_key()
    test_invalid_symbol()

    print(f"\n{'=' * 50}")
    print("  All tests completed.")
    print("=" * 50)
