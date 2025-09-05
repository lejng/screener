import ccxt
from ccxt import Exchange

from src.connectors.common_connector import CommonConnector
from src.connectors.data.base_ticker_info import BaseTickerInfo


class HyperliquidConnector(CommonConnector):

    def __init__(self):
        super().__init__()
        self.spot_exchange = ccxt.hyperliquid()
        self.swap_exchange = ccxt.hyperliquid()
        self.future_exchange = ccxt.hyperliquid()
        self.set_exclude_base({
            "FORM", "ACE",
        })

    def load_spot_symbols(self) -> list[str]:
        return []

    def load_future_symbols(self) -> list[str]:
        return []

    def load_spot_symbols_by_base(self, base: str) -> list[str]:
        return []

    def load_futures_symbols_by_base(self, base: str) -> list[str]:
        return []

    def fetch_future_tickers(self) -> list[BaseTickerInfo]:
        return []

    def fetch_spot_tickers(self) -> list[BaseTickerInfo]:
        return []

    def get_swap_exchange(self) -> Exchange:
        return self.swap_exchange

    def get_spot_exchange(self) -> Exchange:
        return self.spot_exchange

    def get_future_exchange(self) -> Exchange:
        return self.future_exchange

    def get_exchange_name(self) -> str:
        return "HYPERLIQUID"