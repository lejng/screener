from abc import abstractmethod

from ccxt import Exchange
from ccxt.base.types import OrderBook, MarketInterface, Ticker

from src.connectors.common_connector import CommonConnector
from src.connectors.data.base_ticker_info import BaseTickerInfo


class SpotCommonConnector(CommonConnector):

    def __init__(self):
        super().__init__()

    def fetch_order_book(self, symbol: str) -> OrderBook:
        order_book: OrderBook = self.get_exchange().fetch_order_book(symbol=symbol, limit=50, params={'type': 'spot'})
        return order_book

    def fetch_ticker(self, symbol: str) -> BaseTickerInfo:
        ticker: Ticker = self.get_exchange().fetch_ticker(symbol=symbol, params={'type': 'spot'})
        return self.convert_to_ticker_info(ticker, True, False, False)

    def fetch_tickers(self) -> list[BaseTickerInfo]:
        symbols: list[str] = self.load_symbols()
        tickers: dict[str, Ticker] = self.get_exchange().fetch_tickers(symbols=symbols, params={'type': 'spot'})
        return [
            self.convert_to_ticker_info(ticker, True, False, False)
            for ticker in tickers.values()
        ]

    def load_symbols(self) -> list[str]:
        symbols = []
        markets: dict[str, MarketInterface] = self.get_exchange().load_markets()
        for value in markets.values():
            quote = value.get('quote', '')
            base =  value.get('base', '')
            if (value.get('spot', False)
                    and quote in self.get_allowed_quotes()
                    and value.get('active', False)
                    and base not in self.get_exclude_base()):
                    symbols.append(value['symbol'])
        return symbols

    def load_symbols_by_base(self, base: str) -> list[str]:
        symbols = []
        markets: dict[str, MarketInterface] = self.get_exchange().load_markets()
        for value in markets.values():
            quote = value.get('quote', '')
            base_value = value.get('base', '')
            if (base_value.lower() == base.lower()
                    and value.get('spot', False)
                    and quote in self.get_allowed_quotes()):
                symbols.append(value['symbol'])
        return symbols

    @abstractmethod
    def get_exchange(self) -> Exchange:
        pass

    @abstractmethod
    def get_exchange_name(self) -> str:
        pass