"""Tools package for crypto investment assistance."""

import json
from typing import Dict, Any, List

# Import tool functions
from crypto_agent.tools.price_tool import get_crypto_price, get_crypto_price_tool
from crypto_agent.tools.portfolio_tool import get_portfolio, get_portfolio_tool
from crypto_agent.tools.calculator_tool import calculate_investment, calculate_investment_tool
from crypto_agent.tools.coinmarketcap_tool import get_crypto_price_cmc, get_crypto_price_cmc_tool
from crypto_agent.tools.market_data_tool import get_market_data, get_market_data_tool
from crypto_agent.tools.historical_price_tool import get_historical_price, get_historical_price_tool
from crypto_agent.tools.top_movers_tool import get_top_movers, get_top_movers_tool
from crypto_agent.tools.global_market_tool import get_global_market_data, get_global_market_data_tool
from crypto_agent.tools.trending_coins_tool import get_trending_coins, get_trending_coins_tool
from crypto_agent.tools.search_crypto_tool import search_crypto, search_crypto_tool


def get_all_tools() -> List[Dict[str, Any]]:
    """Return all available crypto tools as a list of dicts."""
    return [
        get_crypto_price_tool,
        get_crypto_price_cmc_tool,
        get_portfolio_tool,
        calculate_investment_tool,
        get_market_data_tool,
        get_historical_price_tool,
        get_top_movers_tool,
        get_global_market_data_tool,
        get_trending_coins_tool,
        search_crypto_tool,
    ]


def execute_tool(tool_name: str, **kwargs) -> str:
    """Execute a tool by name and return result string."""
    tool_map = {
        "get_crypto_price": get_crypto_price,
        "get_portfolio": get_portfolio,
        "calculate_investment": calculate_investment,
        "get_market_data": get_market_data,
        "get_crypto_price_cmc": get_crypto_price_cmc,
        "get_historical_price": get_historical_price,
        "get_top_movers": get_top_movers,
        "get_global_market_data": get_global_market_data,
        "get_trending_coins": get_trending_coins,
        "search_crypto": search_crypto,
    }

    if tool_name in tool_map:
        try:
            result = tool_map[tool_name](**kwargs)
            return result
        except Exception as e:
            return json.dumps({"error": f"Tool execution failed: {str(e)}"})

    return json.dumps({"error": f"Tool '{tool_name}' not found"})
