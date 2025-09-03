from abc import ABC, abstractmethod

from ccxt import Exchange
from ccxt.base.types import Ticker, MarketInterface, FundingRate, OrderBook

from src.config.custom_logger import CustomLogger
from src.connectors.data.funding_rate_info import FundingRateInfo
from src.connectors.data.ticker_info import TickerInfo


class CommonConnector(ABC):

    def __init__(self):
        self.logger = CustomLogger()
        # think about property file per connector and read this values
        self.allowed_quotes = { 'USDT', 'USDC' }
        self.exclude_base = set()

    def fetch_top_funding_rates(self, max_count = 10) -> dict[str, list[FundingRateInfo]] :
        rates: list[FundingRateInfo] = self.fetch_funding_rates()
        top_max = sorted(rates, key=lambda x: x.get_funding_rate(), reverse=True)[:max_count]
        top_small = sorted(rates, key=lambda x: x.get_funding_rate(), reverse=False)[:max_count]
        return {'max': top_max, 'small': top_small}

    def fetch_funding_rates(self) -> list[FundingRateInfo]:
        symbols = self.load_swap_symbols()
        rates: dict[str, FundingRate] = self.get_swap_exchange().fetch_funding_rates(symbols=symbols)
        return [
            FundingRateInfo(rate)
            for rate in rates.values()
        ]

    def fetch_funding_rate_by_base(self, base: str) -> list[FundingRateInfo]:
        symbols = self.load_swap_symbols_by_base(base)
        result = []
        for symbol in symbols:
            result.append(self.fetch_funding_rate(symbol))
        return result

    def fetch_funding_rate(self, symbol: str) -> FundingRateInfo:
        rate: FundingRate = self.get_swap_exchange().fetch_funding_rate(symbol)
        return FundingRateInfo(rate)

    def fetch_future_ticker(self, symbol: str) -> TickerInfo:
        ticker: Ticker = self.get_future_exchange().fetch_ticker(symbol=symbol)
        return self.convert_to_ticker_info(ticker, False, False, True)

    def fetch_future_order_book(self, symbol: str) -> OrderBook:
        order_book: OrderBook = self.get_future_exchange().fetch_order_book(symbol=symbol, limit=20)
        return order_book

    def fetch_swap_ticker(self, symbol: str) -> TickerInfo:
        ticker: Ticker = self.get_swap_exchange().fetch_ticker(symbol=symbol, params={'category': 'swap'})
        return self.convert_to_ticker_info(ticker, False, True, False)

    def fetch_swap_order_book(self, symbol: str) -> OrderBook:
        order_book: OrderBook = self.get_swap_exchange().fetch_order_book(symbol=symbol, limit=20, params={'category': 'swap'})
        return order_book

    def fetch_spot_ticker(self, symbol: str) -> TickerInfo:
        ticker: Ticker = self.get_spot_exchange().fetch_ticker(symbol=symbol, params={'type': 'spot'})
        return self.convert_to_ticker_info(ticker, True, False, False)

    def fetch_spot_order_book(self, symbol: str) -> OrderBook:
        order_book: OrderBook = self.get_spot_exchange().fetch_order_book(symbol=symbol, limit=20, params={'type': 'spot'})
        return order_book

    def fetch_future_tickers(self) -> list[TickerInfo]:
        symbols = self.load_future_symbols()
        tickers: dict[str, Ticker] = self.get_future_exchange().fetch_tickers(symbols=symbols)
        return [
            self.convert_to_ticker_info(ticker, False, False, True)
            for ticker in tickers.values()
        ]

    def fetch_swap_tickers(self) -> list[TickerInfo]:
        symbols = self.load_swap_symbols()
        tickers: dict[str, Ticker] = self.get_swap_exchange().fetch_tickers(symbols=symbols, params={'category': 'swap'})
        return [
            self.convert_to_ticker_info(ticker, False, True, False)
            for ticker in tickers.values()
        ]

    def fetch_spot_tickers(self) -> list[TickerInfo]:
        symbols: list[str] = self.load_spot_symbols()
        tickers: dict[str, Ticker] = self.get_spot_exchange().fetch_tickers(symbols=symbols, params={'type': 'spot'})
        return [
            self.convert_to_ticker_info(ticker, True, False, False)
            for ticker in tickers.values()
        ]

    def convert_to_ticker_info(self, ticker: Ticker, spot: bool, swap: bool, future: bool) -> TickerInfo:
        base, quote = self.parse_symbol(ticker)
        return TickerInfo(
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

    def load_future_market(self) -> dict[str, MarketInterface]:
        return self.get_future_exchange().load_markets()

    def load_swap_market(self) -> dict[str, MarketInterface]:
        return self.get_swap_exchange().load_markets()

    def load_spot_market(self) -> dict[str, MarketInterface]:
        return self.get_spot_exchange().load_markets()

    def load_spot_symbols(self) -> list[str]:
        symbols = []
        markets: dict[str, MarketInterface] = self.load_spot_market()
        for value in markets.values():
            quote = value.get('quote', '')
            base =  value.get('base', '')
            if (value.get('spot', False)
                    and quote in self.get_allowed_quotes()
                    and value.get('active', False)
                    and base not in self.get_exclude_base()):
                    symbols.append(value['symbol'])
        return symbols

    def load_future_symbols(self) -> list[str]:
        symbols = []
        markets: dict[str, MarketInterface] = self.load_future_market()
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

    def load_swap_symbols(self) -> list[str]:
        symbols = []
        markets: dict[str, MarketInterface] = self.load_swap_market()
        for value in markets.values():
            quote = value.get('quote', '')
            base =  value.get('base', '')
            if (value.get('swap', False)
                    and quote in self.get_allowed_quotes()
                    and value.get('active', False)
                    and base not in self.get_exclude_base()):
                    symbols.append(value['symbol'])
        return symbols

    def load_swap_symbols_by_base(self, base: str) -> list[str]:
        symbols = []
        markets: dict[str, MarketInterface] = self.load_swap_market()
        for value in markets.values():
            quote = value.get('quote', '')
            base_value = value.get('base', '')
            if (base_value.lower() == base.lower()
                    and value.get('swap', False)
                    and value.get('active', False)
                    and quote in self.get_allowed_quotes()):
                symbols.append(value['symbol'])
        return symbols

    def load_spot_symbols_by_base(self, base: str) -> list[str]:
        symbols = []
        markets: dict[str, MarketInterface] = self.load_spot_market()
        for value in markets.values():
            quote = value.get('quote', '')
            base_value = value.get('base', '')
            if (base_value.lower() == base.lower()
                    and value.get('spot', False)
                    and quote in self.get_allowed_quotes()):
                symbols.append(value['symbol'])
        return symbols

    def load_futures_symbols_by_base(self, base: str) -> list[str]:
        symbols = []
        markets: dict[str, MarketInterface] = self.load_future_market()
        for value in markets.values():
            base_value = value.get('base', '')
            if (base_value.lower() == base.lower()
                    and value.get('active', False)
                    and (value.get('future', False) or value.get('inverse', False))):
                symbols.append(value['symbol'])
        return symbols

    def paginate(self, list_data, page_size: int) -> list:
        pages = []
        for index in range(0, len(list_data), page_size):
            end_index = index + page_size
            pages.append(list_data[index:end_index])
        return pages

    @abstractmethod
    def get_swap_exchange(self) -> Exchange:
        pass

    @abstractmethod
    def get_future_exchange(self) -> Exchange:
        pass

    @abstractmethod
    def get_spot_exchange(self) -> Exchange:
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