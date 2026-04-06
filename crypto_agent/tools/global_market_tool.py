"""Tool: Get global crypto market data via CoinGecko API."""
import json
import requests
from typing import Dict, Any

def get_global_market_data() -> str:
    url = "https://api.coingecko.com/api/v3/global"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "data" not in data:
            return json.dumps({"error": "No global market data found"})
            
        market_data = data["data"]
        return json.dumps({
            "active_cryptocurrencies": market_data.get("active_cryptocurrencies"),
            "markets": market_data.get("markets"),
            "total_market_cap_usd": market_data.get("total_market_cap", {}).get("usd"),
            "total_volume_usd": market_data.get("total_volume", {}).get("usd"),
            "market_cap_percentage_btc": market_data.get("market_cap_percentage", {}).get("btc"),
            "market_cap_percentage_eth": market_data.get("market_cap_percentage", {}).get("eth"),
            "market_cap_change_percentage_24h_usd": market_data.get("market_cap_change_percentage_24h_usd")
        })
    except requests.RequestException as e:
        return json.dumps({"error": f"Failed to fetch global market data from CoinGecko: {str(e)}"})

get_global_market_data_tool = {
    "name": "get_global_market_data",
    "description": "Get global cryptocurrency market metrics including total market cap, trading volume, and Bitcoin dominance. No inputs required."
}
