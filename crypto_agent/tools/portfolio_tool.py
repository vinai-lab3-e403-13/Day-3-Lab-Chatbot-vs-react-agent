"""Tool: Get user's portfolio balance (mock data)."""

import json
from typing import Dict, Any


MOCK_PORTFOLIOS = {
    "default": {
        "total_value_usd": 10500.00,
        "holdings": [
            {"crypto": "bitcoin", "amount": 0.15, "value_usd": 6000.00},
            {"crypto": "ethereum", "amount": 2.5, "value_usd": 3500.00},
            {"crypto": "solana", "amount": 50, "value_usd": 1000.00}
        ]
    }
}


def get_portfolio(user_id: str = "default") -> str:
    """
    Get user's crypto portfolio balance and holdings.

    Args:
        user_id: User identifier (defaults to 'default')

    Returns:
        JSON string with portfolio data
    """
    portfolio = MOCK_PORTFOLIOS.get(user_id, MOCK_PORTFOLIOS["default"])
    return json.dumps(portfolio)


get_portfolio_tool = {
    "name": "get_portfolio",
    "description": "Get user's current portfolio balance and holdings. Input: user_id (optional, defaults to 'default'). Returns total value in USD and list of holdings with amounts."
}
