"""Tool: Get current price of a cryptocurrency via CoinGecko API."""

import json
import requests
from typing import Dict, Any

def get_crypto_price(crypto_id: str) -> str:
    """
    Get the current price of a cryptocurrency in USD.

    Args:
        crypto_id: CoinGecko ID (e.g., 'bitcoin', 'ethereum', 'solana', 'cardano')

    Returns:
        JSON string with price data
    """
    crypto_id_lower = crypto_id.lower()
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": crypto_id_lower,
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if crypto_id_lower in data:
            coin_data = data[crypto_id_lower]
            return json.dumps({
                "crypto": crypto_id_lower,
                "price_usd": coin_data.get("usd"),
                "change_24h": coin_data.get("usd_24h_change")
            })
        else:
            return json.dumps({"error": f"Cryptocurrency '{crypto_id}' not found"})
    except requests.RequestException as e:
        return json.dumps({"error": f"Failed to fetch data from CoinGecko: {str(e)}"})


get_crypto_price_tool = {
    "name": "get_crypto_price",
    "description": "Get current price and 24h change of a cryptocurrency. Input: crypto_id (e.g., 'bitcoin', 'ethereum', 'solana', 'cardano'). Returns price in USD and 24h percentage change."
}
