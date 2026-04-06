"""Tool: Get detailed market data of a cryptocurrency via CoinGecko API."""

import json
import requests
from typing import Dict, Any


def get_market_data(crypto_id: str) -> str:
    """
    Get detailed market data of a cryptocurrency in USD.

    Args:
        crypto_id: CoinGecko ID (e.g., 'bitcoin', 'ethereum', 'solana')

    Returns:
        JSON string with detailed market data
    """
    crypto_id_lower = crypto_id.lower()
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": crypto_id_lower
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return json.dumps({"error": f"Cryptocurrency '{crypto_id}' not found"})
        
        coin_data = data[0]
        
        return json.dumps({
            "crypto_name": coin_data.get("name"),
            "symbol": coin_data.get("symbol"),
            "current_price_usd": coin_data.get("current_price"),
            "market_cap_usd": coin_data.get("market_cap"),
            "market_cap_rank": coin_data.get("market_cap_rank"),
            "total_volume_usd_24h": coin_data.get("total_volume"),
            "high_24h_usd": coin_data.get("high_24h"),
            "low_24h_usd": coin_data.get("low_24h"),
            "price_change_percentage_24h": coin_data.get("price_change_percentage_24h"),
            "circulating_supply": coin_data.get("circulating_supply"),
            "max_supply": coin_data.get("max_supply"),
            "all_time_high_usd": coin_data.get("ath")
        })
    except requests.RequestException as e:
        return json.dumps({"error": f"Failed to fetch market data from CoinGecko: {str(e)}"})


get_market_data_tool = {
    "name": "get_market_data",
    "description": "Get detailed market data for a cryptocurrency including market cap, 24h volume, circulating supply, all-time high, market cap rank, and high/low prices. Input: crypto_id (e.g., 'bitcoin'). Returns detailed JSON market data."
}
