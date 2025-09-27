from abc import abstractmethod

from ccxt import Exchange
from ccxt.base.types import MarketInterface, Ticker, OrderBook

from src.connectors.common_connector import CommonConnector
from src.connectors.data.base_ticker_info import BaseTickerInfo


class FutureCommonConnector(CommonConnector):

    def __init__(self):
        super().__init__()

    def fetch_order_book(self, symbol: str) -> OrderBook:
        order_book: OrderBook = self.get_exchange().fetch_order_book(symbol=symbol, limit=50)
        return order_book

    def fetch_ticker(self, symbol: str) -> BaseTickerInfo:
        ticker: Ticker = self.get_exchange().fetch_ticker(symbol=symbol)
        return self.convert_to_ticker_info(ticker, False, False, True)

    def fetch_tickers(self) -> list[BaseTickerInfo]:
        symbols = self.load_symbols()
        tickers: dict[str, Ticker] = self.get_exchange().fetch_tickers(symbols=symbols)
        return [
            self.convert_to_ticker_info(ticker, False, False, True)
            for ticker in tickers.values()
        ]

    def load_symbols(self) -> list[str]:
        symbols = []
        markets: dict[str, MarketInterface] = self.get_exchange().load_markets()
        for value in markets.values():
            quote = value.get('quote', '')
            base =  value.get('base', '')
            if ((value.get('future', False)
                 or value.get('inverse', False))
                    and quote in self.get_allowed_quotes()
                    and value.get('active', False)
                    and base not in self.get_exclude_base()):
                    symbols.append(value['symbol'])
        return symbols

    def load_symbols_by_base(self, base: str) -> list[str]:
        symbols = []
        markets: dict[str, MarketInterface] = self.get_exchange().load_markets()
        for value in markets.values():
            base_value = value.get('base', '')
            if (base_value.lower() == base.lower()
                    and value.get('active', False)
                    and (value.get('future', False) or value.get('inverse', False))):
                symbols.append(value['symbol'])
        return symbols

    @abstractmethod
    def get_exchange(self) -> Exchange:
        pass

    @abstractmethod
    def get_exchange_name(self) -> str:
        pass