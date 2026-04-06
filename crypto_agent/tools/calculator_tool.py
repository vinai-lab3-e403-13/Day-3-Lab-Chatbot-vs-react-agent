"""Tool: Calculate potential investment returns."""

import json
from typing import Dict, Any


MOCK_PRICES = {
    "bitcoin": 67000.0,
    "ethereum": 2800.0,
    "solana": 140.0,
    "cardano": 0.45
}


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
    price = MOCK_PRICES.get(crypto_id, None)

    if price is None:
        return json.dumps({"error": f"Cryptocurrency '{crypto_id}' not found in calculator"})

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
