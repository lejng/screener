import ccxt
from ccxt import Exchange
from ccxt.base.types import Ticker

from src.connectors.common_connector import CommonConnector, TickerInfo


class BinanceConnector(CommonConnector):

    def __init__(self):
        super().__init__()
        self.spot_exchange = ccxt.binance({'options': {'defaultType': 'spot'}})
        self.swap_exchange = ccxt.binanceusdm()
        self.future_exchange = ccxt.binanceusdm()
        self.set_exclude_base(set())

    def fetch_spot_tickers(self) -> list[TickerInfo]:
        symbols: list[str] = self.load_spot_symbols()
        symbol_pages: list[list[str]] = self.paginate(symbols, 400)
        tickers: dict[str, Ticker] = {}
        for symbol_page in symbol_pages:
            tickers.update(self.get_spot_exchange().fetch_tickers(symbols=symbol_page, params={'type': 'spot'}))
        return [
            self.convert_to_ticker_info(ticker, True, False, False)
            for ticker in tickers.values()
        ]

    def get_swap_exchange(self) -> Exchange:
        return self.swap_exchange

    def get_spot_exchange(self) -> Exchange:
        return self.spot_exchange

    def get_future_exchange(self) -> Exchange:
        return self.future_exchange

    def get_exchange_name(self) -> str:
        return "BINANCE"