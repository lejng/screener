from abc import ABC, abstractmethod

from ccxt import Exchange
from ccxt.base.types import Ticker, OrderBook

from src.config.custom_logger import CustomLogger
from src.connectors.data.base_ticker_info import BaseTickerInfo
from src.connectors.data.market_candle import MarketCandle


class CommonConnector(ABC):

    def __init__(self):
        self.logger = CustomLogger()
        # think about property file per connector and read this values
        self.allowed_quotes = { 'USDT', 'USDC' }
        self.exclude_base = set()

    def fetch_ohlcv(self, symbol: str, limit: int, timeframe: str = '1m') -> list[MarketCandle]:
        try:
            ohlcv_data = self.get_exchange().fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit = limit)
            return [MarketCandle(*data) for data in ohlcv_data]
        except Exception as e:
            self.logger.log_error(f"Error fetch ohlcv: {symbol}, exchange: {self.get_exchange_name()}, exception: {e}")
            return []

    def convert_to_ticker_info(self, ticker: Ticker, spot: bool, swap: bool, future: bool) -> BaseTickerInfo:
        base, quote = self.parse_symbol(ticker)
        return BaseTickerInfo(
            ticker=ticker,
            exchange_name=self.get_exchange_name(),
            spot=spot,
            swap=swap,
            future=future,
            base_currency=base,
            quote_currency=quote
        )

    def parse_symbol(self, ticker: Ticker) -> tuple[str, str]:
        symbol: str = ticker.get('symbol', '')
        try:
            if symbol == 'MX_USDT':
                return 'MX', 'USDT'
            parts = symbol.replace(':', '/').split('/')
            return parts[0], parts[1]
        except (AttributeError, IndexError):
            self.logger.log_info(f"Error symbol format: {symbol}, exchange: {self.get_exchange_name()}")
            return 'UNKNOWN', 'UNKNOWN'

    def paginate(self, list_data, page_size: int) -> list:
        pages = []
        for index in range(0, len(list_data), page_size):
            end_index = index + page_size
            pages.append(list_data[index:end_index])
        return pages

    @abstractmethod
    def fetch_order_book(self, symbol: str) -> OrderBook:
        pass

    @abstractmethod
    def fetch_ticker(self, symbol: str) -> BaseTickerInfo:
        pass

    @abstractmethod
    def fetch_tickers(self) -> list[BaseTickerInfo]:
        pass

    @abstractmethod
    def load_symbols(self) -> list[str]:
        pass

    def load_symbols_by_base(self, base: str)-> list[str]:
        pass

    @abstractmethod
    def get_exchange(self) -> Exchange:
        pass

    @abstractmethod
    def get_exchange_name(self) -> str:
        pass

    def get_allowed_quotes(self) -> set[str]:
        return self.allowed_quotes

    def get_exclude_base(self) -> set[str]:
        return self.exclude_base

    def set_allowed_quotes(self, allowed_quotes):
        self.allowed_quotes = allowed_quotes

    def set_exclude_base(self, exclude_base: set[str]):
        self.exclude_base = exclude_base