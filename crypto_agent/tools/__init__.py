"""Tools package for crypto investment assistance."""

import json
from typing import Dict, Any, List

# Import tool functions
from crypto_agent.tools.price_tool import get_crypto_price, get_crypto_price_tool
from crypto_agent.tools.portfolio_tool import get_portfolio, get_portfolio_tool
from crypto_agent.tools.calculator_tool import calculate_investment, calculate_investment_tool
from crypto_agent.tools.coinmarketcap_tool import get_crypto_price_cmc, get_crypto_price_cmc_tool


def get_all_tools() -> List[Dict[str, Any]]:
    """Return all available crypto tools as a list of dicts."""
    return [
        get_crypto_price_tool,
        get_crypto_price_cmc_tool,
        get_portfolio_tool,
        calculate_investment_tool,
    ]


def execute_tool(tool_name: str, **kwargs) -> str:
    """Execute a tool by name and return result string."""
    tool_map = {
        "get_crypto_price": get_crypto_price,
        "get_portfolio": get_portfolio,
        "calculate_investment": calculate_investment,
    }

    if tool_name in tool_map:
        try:
            result = tool_map[tool_name](**kwargs)
            return result
        except Exception as e:
            return json.dumps({"error": f"Tool execution failed: {str(e)}"})

    return json.dumps({"error": f"Tool '{tool_name}' not found"})
