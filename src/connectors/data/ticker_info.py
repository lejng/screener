from dataclasses import dataclass

from ccxt.base.types import Ticker


@dataclass
class TickerInfo:
    ticker: Ticker
    exchange_name: str
    spot: bool
    swap: bool
    future: bool
    base_currency: str
    quote_currency: str

    def get_symbol(self) -> str:
        return self.ticker["symbol"]

    def get_buy_price(self):
        if self.ticker["ask"] is not None:
            return self.ticker["ask"]
        return self.ticker["last"]

    def get_sell_price(self):
        if self.ticker["bid"] is not None:
            return self.ticker["bid"]
        return self.ticker["last"]

    def get_ask(self):
        return self.ticker["ask"]

    def get_bid(self):
        return self.ticker["bid"]

    def get_last_price(self):
        return self.ticker["last"]

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