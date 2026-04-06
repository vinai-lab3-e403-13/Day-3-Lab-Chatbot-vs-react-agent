"""Tool: Get current price of a cryptocurrency via CoinMarketCap API."""

import json
import os
import requests
from typing import Optional

# CoinMarketCap API base URL
CMC_BASE_URL = "https://pro-api.coinmarketcap.com/v1"

# Symbol mapping for common coins (CoinMarketCap uses ticker symbols)
SYMBOL_ALIASES = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "cardano": "ADA",
    "binancecoin": "BNB",
    "ripple": "XRP",
    "dogecoin": "DOGE",
    "polkadot": "DOT",
    "avalanche": "AVAX",
    "chainlink": "LINK",
}


def get_crypto_price_cmc(crypto_id: str, api_key: Optional[str] = None) -> str:
    """
    Get the current price of a cryptocurrency from CoinMarketCap.

    Args:
        crypto_id: Coin name (e.g., 'bitcoin', 'ethereum') or ticker symbol (e.g., 'BTC', 'ETH')
        api_key: CoinMarketCap API key. Falls back to CMC_API_KEY environment variable.

    Returns:
        JSON string with price data including price_usd, market_cap, volume_24h, change_24h
    """
    key = api_key or os.environ.get("CMC_API_KEY", "")
    if not key:
        return json.dumps({
            "error": "CoinMarketCap API key not found. Set the CMC_API_KEY environment variable."
        })

    # Resolve alias (e.g., "bitcoin" -> "BTC")
    symbol = SYMBOL_ALIASES.get(crypto_id.lower(), crypto_id.upper())

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": key,
    }
    params = {
        "symbol": symbol,
        "convert": "USD",
    }

    try:
        response = requests.get(
            f"{CMC_BASE_URL}/cryptocurrency/quotes/latest",
            headers=headers,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status", {}).get("error_code", 0) != 0:
            error_msg = data["status"].get("error_message", "Unknown API error")
            return json.dumps({"error": error_msg})

        coin_data = data.get("data", {}).get(symbol)
        if not coin_data:
            return json.dumps({"error": f"Symbol '{symbol}' not found on CoinMarketCap"})

        quote = coin_data["quote"]["USD"]
        return json.dumps({
            "crypto": coin_data["name"],
            "symbol": coin_data["symbol"],
            "price_usd": round(quote["price"], 6),
            "market_cap_usd": round(quote["market_cap"], 2),
            "volume_24h_usd": round(quote["volume_24h"], 2),
            "change_1h": round(quote["percent_change_1h"], 2),
            "change_24h": round(quote["percent_change_24h"], 2),
            "change_7d": round(quote["percent_change_7d"], 2),
            "last_updated": quote["last_updated"],
        })

    except requests.exceptions.Timeout:
        return json.dumps({"error": "Request timed out. CoinMarketCap API did not respond in time."})
    except requests.exceptions.ConnectionError:
        return json.dumps({"error": "Connection error. Could not reach CoinMarketCap API."})
    except requests.exceptions.HTTPError as e:
        return json.dumps({"error": f"HTTP error: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"})


get_crypto_price_cmc_tool = {
    "name": "get_crypto_price_cmc",
    "description": (
        "Get real-time price data for a cryptocurrency from CoinMarketCap. "
        "Input: crypto_id — coin name (e.g., 'bitcoin', 'ethereum', 'solana') or ticker symbol (e.g., 'BTC', 'ETH', 'SOL'). "
        "Returns: price in USD, market cap, 24h trading volume, and percentage change over 1h / 24h / 7d."
    ),
}
