"""Tool: Search for a cryptocurrency ID by name or symbol via CoinGecko API."""
import json
import requests
from typing import Dict, Any

def search_crypto(query: str) -> str:
    url = "https://api.coingecko.com/api/v3/search"
    params = {"query": query}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get("coins"):
            return json.dumps({"error": f"No coins found matching query: '{query}'"})
            
        results = []
        for coin in data["coins"][:5]: # Return top 5 matches
            results.append({
                "id": coin.get("id"),
                "name": coin.get("name"),
                "symbol": coin.get("symbol"),
                "market_cap_rank": coin.get("market_cap_rank")
            })
            
        return json.dumps({"search_results": results})
    except requests.RequestException as e:
        return json.dumps({"error": f"Failed to execute search on CoinGecko: {str(e)}"})

search_crypto_tool = {
    "name": "search_crypto",
    "description": "Search for a cryptocurrency by name or symbol (e.g., 'pepe', 'bnb') to find its CoinGecko ID. Input: query (str). Returns a list of top 5 matching coins with their IDs."
}
