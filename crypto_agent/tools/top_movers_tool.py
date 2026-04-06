"""Tool: Get top gaining and losing cryptocurrencies via CoinGecko API."""
import json
import requests
from typing import Dict, Any

def get_top_movers(limit: int = 5) -> str:
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
             return json.dumps({"error": "No market data found"})
             
        sorted_by_change = sorted([c for c in data if c.get("price_change_percentage_24h") is not None], 
                                  key=lambda x: x.get("price_change_percentage_24h", 0), reverse=True)
                                  
        top_gainers = [{"symbol": c["symbol"], "price_usd": c["current_price"], "change_24h": round(c["price_change_percentage_24h"], 2)} for c in sorted_by_change[:limit]]
        top_losers = [{"symbol": c["symbol"], "price_usd": c["current_price"], "change_24h": round(c["price_change_percentage_24h"], 2)} for c in sorted_by_change[-limit:]]
        
        return json.dumps({
            "top_gainers": top_gainers,
            "top_losers": top_losers
        })
    except requests.RequestException as e:
        return json.dumps({"error": f"Failed to fetch top movers from CoinGecko: {str(e)}"})

get_top_movers_tool = {
    "name": "get_top_movers",
    "description": "Get top gaining and losing cryptocurrencies by 24h percentage change from the top 100 coins. Input: limit (int, optional, defaults to 5). Returns lists of top gainers and losers."
}
