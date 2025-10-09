from dataclasses import dataclass
from typing import Optional

from ccxt.base.types import Ticker

from src.connectors.data.funding_rate_info import FundingRateInfo


@dataclass
class BaseTickerInfo:
    ticker: Ticker
    exchange_name: str
    spot: bool
    swap: bool
    future: bool
    base_currency: str
    quote_currency: str

    def get_symbol(self) -> str:
        return self.ticker["symbol"]

    def get_best_buy_price(self) -> Optional[float]:
        return self.ticker.get("ask") or self.ticker.get("last")

    def get_best_sell_price(self) -> Optional[float]:
        return self.ticker.get("bid") or self.ticker.get("last")

    def get_coins_to_buy(self) -> Optional[float]:
        return None

    def get_coins_to_sell(self) -> Optional[float]:
        return None

    def get_funding_info(self) -> Optional[FundingRateInfo]:
        return None

    def get_amount_in_quote(self) -> Optional[float]:
        return None

    def get_market_type(self) -> str:
        if self.spot:
            return "spot"
        if self.swap:
            return "swap"
        if self.future:
            return "future"
        return "unknown"

    def get_trading_view_name(self) -> str:
        if self.spot:
            return f"{self.exchange_name}:{self.base_currency}{self.quote_currency}"
        if self.swap:
            return f"{self.exchange_name}:{self.base_currency}{self.quote_currency}.P"
        if self.future:
            return f"{self.exchange_name}:{self.get_symbol()}"
        return f"{self.exchange_name}:{self.base_currency}{self.quote_currency}.UNKNOWN"