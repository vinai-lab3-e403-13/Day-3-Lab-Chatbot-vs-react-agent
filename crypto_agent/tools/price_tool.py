"""Tool: Get current price of a cryptocurrency via CoinGecko API."""

import json
from typing import Dict, Any

# Mock prices for demo purposes (CoinGecko API can be used with requests library)
MOCK_PRICES = {
    "bitcoin": {"price_usd": 67500.00, "change_24h": 2.35},
    "ethereum": {"price_usd": 3450.00, "change_24h": -1.20},
    "solana": {"price_usd": 145.00, "change_24h": 5.80},
    "cardano": {"price_usd": 0.48, "change_24h": -0.50},
}


def get_crypto_price(crypto_id: str) -> str:
    """
    Get the current price of a cryptocurrency in USD.

    Args:
        crypto_id: CoinGecko ID (e.g., 'bitcoin', 'ethereum', 'solana', 'cardano')

    Returns:
        JSON string with price data
    """
    crypto_id_lower = crypto_id.lower()
    if crypto_id_lower in MOCK_PRICES:
        data = MOCK_PRICES[crypto_id_lower]
        return json.dumps({
            "crypto": crypto_id_lower,
            "price_usd": data["price_usd"],
            "change_24h": data["change_24h"]
        })
    return json.dumps({"error": f"Cryptocurrency '{crypto_id}' not found"})


get_crypto_price_tool = {
    "name": "get_crypto_price",
    "description": "Get current price and 24h change of a cryptocurrency. Input: crypto_id (e.g., 'bitcoin', 'ethereum', 'solana', 'cardano'). Returns price in USD and 24h percentage change."
}
