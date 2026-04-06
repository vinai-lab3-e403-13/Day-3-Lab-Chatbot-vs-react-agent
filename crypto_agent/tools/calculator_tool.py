"""Tool: Calculate potential investment returns."""

import json
import requests
from typing import Dict, Any


def calculate_investment(amount_usd: float, crypto_id: str, expected_gain_pct: float = 0.0) -> str:
    """
    Calculate potential returns for a crypto investment.

    Args:
        amount_usd: Amount to invest in USD
        crypto_id: Cryptocurrency to invest in
        expected_gain_pct: Expected price gain percentage (optional)

    Returns:
        JSON string with calculation results
    """
    crypto_id_lower = crypto_id.lower()
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": crypto_id_lower,
        "vs_currencies": "usd"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if crypto_id_lower not in data or "usd" not in data[crypto_id_lower]:
            return json.dumps({"error": f"Cryptocurrency '{crypto_id}' not found in CoinGecko"})
            
        price = data[crypto_id_lower]["usd"]
    except requests.RequestException as e:
        return json.dumps({"error": f"Failed to fetch current pricing from CoinGecko: {str(e)}"})

    amount_crypto = amount_usd / price

    result = {
        "investment_usd": amount_usd,
        "crypto_id": crypto_id,
        "amount_crypto": round(amount_crypto, 8),
        "current_price": price
    }

    if expected_gain_pct > 0:
        final_value = amount_usd * (1 + expected_gain_pct / 100)
        result["expected_gain_pct"] = expected_gain_pct
        result["final_value_usd"] = round(final_value, 2)
        result["profit_usd"] = round(final_value - amount_usd, 2)

    return json.dumps(result)


calculate_investment_tool = {
    "name": "calculate_investment",
    "description": "Calculate potential investment returns. Inputs: amount_usd (float), crypto_id (str), expected_gain_pct (float, optional). Returns amount of crypto purchased, current price, and optional projected final value with profit."
}
