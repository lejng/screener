import ccxt
from ccxt import Exchange
from ccxt.base.types import Ticker

from src.connectors.common_connector import CommonConnector, TickerInfo


class BybitConnector(CommonConnector):

    def __init__(self):
        super().__init__()
        self.spot_exchange = ccxt.bybit({'options': {'defaultType': 'spot'}})
        self.swap_exchange = ccxt.bybit({'options': {'defaultType': 'swap'}})
        self.future_exchange = ccxt.bybit({'options': {'defaultType': 'inverse'}})
        self.set_exclude_base({
            "NEIRO","TRC"
        })

    def fetch_swap_tickers(self) -> list[TickerInfo]:
        symbols = self.load_swap_symbols()
        tickers: dict[str, Ticker] = self.get_swap_exchange().fetch_tickers(symbols=symbols, params={'category': 'linear'})
        return [
            self.convert_to_ticker_info(ticker, False, True, False)
            for ticker in tickers.values()
        ]

    def get_swap_exchange(self) -> Exchange:
        return self.swap_exchange

    def get_spot_exchange(self) -> Exchange:
        return self.spot_exchange

    def get_future_exchange(self) -> Exchange:
        return self.future_exchange

    def get_exchange_name(self) -> str:
        return "BYBIT"