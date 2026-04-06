"""Tool: Get trending cryptocurrencies via CoinGecko API."""
import json
import requests
from typing import Dict, Any

def get_trending_coins() -> str:
    url = "https://api.coingecko.com/api/v3/search/trending"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "coins" not in data:
            return json.dumps({"error": "No trending data found"})
            
        trending = []
        for item in data["coins"][:7]: # Limit to top 7
            coin = item["item"]
            trending.append({
                "id": coin.get("id"),
                "name": coin.get("name"),
                "symbol": coin.get("symbol"),
                "market_cap_rank": coin.get("market_cap_rank"),
                "price_btc": coin.get("price_btc")
            })
            
        return json.dumps({"trending_coins": trending})
    except requests.RequestException as e:
        return json.dumps({"error": f"Failed to fetch trending coins from CoinGecko: {str(e)}"})

get_trending_coins_tool = {
    "name": "get_trending_coins",
    "description": "Get the top-7 trending searched coins on CoinGecko in the last 24 hours. No inputs required."
}
