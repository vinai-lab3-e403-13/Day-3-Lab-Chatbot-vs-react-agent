"""Tool: Get user's portfolio balance (mock data)."""

import json
import requests
from typing import Dict, Any

USER_PORTFOLIOS = {
    "default": {
        "bitcoin": 0.15,
        "ethereum": 2.5,
        "solana": 50
    }
}


def get_portfolio(user_id: str = "default") -> str:
    """
    Get user's crypto portfolio balance and holdings based on real-time prices.

    Args:
        user_id: User identifier (defaults to 'default')

    Returns:
        JSON string with portfolio data
    """
    portfolio_amounts = USER_PORTFOLIOS.get(user_id, USER_PORTFOLIOS["default"])
    
    crypto_ids = list(portfolio_amounts.keys())
    ids_str = ",".join(crypto_ids)
    
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ids_str,
        "vs_currencies": "usd"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        prices_data = response.json()
        
        total_value_usd = 0.0
        holdings = []
        
        for crypto_id, amount in portfolio_amounts.items():
            price = prices_data.get(crypto_id, {}).get("usd", 0.0)
            value_usd = price * amount
            total_value_usd += value_usd
            
            holdings.append({
                "crypto": crypto_id,
                "amount": amount,
                "current_price_usd": price,
                "value_usd": value_usd
            })
            
        return json.dumps({
            "total_value_usd": total_value_usd,
            "holdings": holdings
        })
            
    except requests.RequestException as e:
        return json.dumps({"error": f"Failed to fetch current pricing data from CoinGecko: {str(e)}"})


get_portfolio_tool = {
    "name": "get_portfolio",
    "description": "Get user's current portfolio balance and holdings. Input: user_id (optional, defaults to 'default'). Returns total value in USD and list of holdings with amounts."
}
