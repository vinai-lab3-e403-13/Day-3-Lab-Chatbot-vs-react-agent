"""Tool: Get historical price data of a cryptocurrency via CoinGecko API."""
import json
import requests
from typing import Dict, Any

def get_historical_price(crypto_id: str, date: str) -> str:
    # date format: dd-mm-yyyy
    crypto_id_lower = crypto_id.lower()
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id_lower}/history"
    params = {"date": date}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "market_data" not in data:
            return json.dumps({"error": f"No historical market data found for {crypto_id} on {date}"})
        return json.dumps({
            "crypto_id": crypto_id_lower,
            "date": date,
            "price_usd": data["market_data"]["current_price"]["usd"]
        })
    except requests.RequestException as e:
        return json.dumps({"error": f"Failed to fetch historical data from CoinGecko: {str(e)}"})

get_historical_price_tool = {
    "name": "get_historical_price",
    "description": "Get historical price of a cryptocurrency on a specific date. Input: crypto_id (str), date (str, format: 'dd-mm-yyyy'). Returns historical price in USD."
}
