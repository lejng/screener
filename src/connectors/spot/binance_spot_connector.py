import ccxt
from ccxt import Exchange
from ccxt.base.types import Ticker, OrderBook

from src.connectors.data.base_ticker_info import BaseTickerInfo
from src.connectors.spot.spot_common_connector import SpotCommonConnector


class BinanceSpotConnector(SpotCommonConnector):

    def __init__(self):
        super().__init__()
        self.exchange = ccxt.binance({'options': {'defaultType': 'spot'}})

    def fetch_ticker(self, symbol: str) -> BaseTickerInfo:
        ticker: Ticker = self.get_exchange().fetch_ticker(symbol=symbol)
        return self.convert_to_ticker_info(ticker, True, False, False)

    def fetch_order_book(self, symbol: str) -> OrderBook:
        order_book: OrderBook = self.get_exchange().fetch_order_book(symbol=symbol, limit=50)
        return order_book

    def fetch_tickers(self) -> list[BaseTickerInfo]:
        symbols: list[str] = self.load_symbols()
        symbol_pages: list[list[str]] = self.paginate(symbols, 400)
        tickers: dict[str, Ticker] = {}
        for symbol_page in symbol_pages:
            tickers.update(self.get_exchange().fetch_tickers(symbols=symbol_page, params={'type': 'spot'}))
        return [
            self.convert_to_ticker_info(ticker, True, False, False)
            for ticker in tickers.values()
        ]

    def get_exchange(self) -> Exchange:
        return self.exchange

    def get_exchange_name(self) -> str:
        return "BINANCE"