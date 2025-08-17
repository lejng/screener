from abc import ABC, abstractmethod
from dataclasses import dataclass

from ccxt import Exchange
from ccxt.base.types import Ticker, MarketInterface, FundingRate, TypedDict

from src.config.custom_logger import CustomLogger

@dataclass
class TickerInfo:
    ticker: Ticker
    exchange_name: str
    spot: bool
    swap: bool
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
        return "unknown"

    def get_trading_view_name(self) -> str:
        if self.spot:
            return f"{self.exchange_name}:{self.base_currency}{self.quote_currency}"
        if self.swap:
            return f"{self.exchange_name}:{self.base_currency}{self.quote_currency}.P"
        return f"{self.exchange_name}:{self.base_currency}{self.quote_currency}.UNKNOWN"

class CommonConnector(ABC):

    def __init__(self):
        self.logger = CustomLogger()
        # think about property file per connector and read this values
        self.allowed_quotes = { 'USDT', 'USDC' }
        self.exclude_base = set()

    def fetch_sorted_funding_rates(self, max_count = 10) -> dict[str, list[FundingRate]] :
        rates: list[FundingRate] = list(self.fetch_funding_rates().values())
        top_max = sorted(rates, key=lambda x: x['fundingRate'], reverse=True)[:max_count]
        top_small = sorted(rates, key=lambda x: x['fundingRate'], reverse=False)[:max_count]
        return {'max': top_max, 'small': top_small}

    def fetch_funding_rates(self) -> dict[str, FundingRate]:
        symbols = self.load_swap_symbols()
        return self.get_swap_exchange().fetch_funding_rates(symbols=symbols)

    def fetch_swap_tickers(self) -> list[TickerInfo]:
        symbols = self.load_swap_symbols()
        tickers: dict[str, Ticker] = self.get_swap_exchange().fetch_tickers(symbols=symbols, params={'category': 'swap'})
        return [
            self.convert_to_ticker_info(ticker, False, True)
            for ticker in tickers.values()
        ]

    def fetch_spot_tickers(self) -> list[TickerInfo]:
        symbols: list[str] = self.load_spot_symbols()
        tickers: dict[str, Ticker] = self.get_spot_exchange().fetch_tickers(symbols=symbols, params={'type': 'spot'})
        return [
            self.convert_to_ticker_info(ticker, True, False)
            for ticker in tickers.values()
        ]

    def convert_to_ticker_info(self, ticker: Ticker, spot: bool, swap: bool) -> TickerInfo:
        base, quote = self.parse_symbol(ticker)
        return TickerInfo(
            ticker=ticker,
            exchange_name=self.get_exchange_name(),
            spot=spot,
            swap=swap,
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
            if value.get('spot', False) and quote in self.get_allowed_quotes() and value.get('active', False) and base not in self.get_exclude_base():
                    symbols.append(value['symbol'])
        return symbols

    def load_swap_symbols(self) -> list[str]:
        symbols = []
        markets: dict[str, MarketInterface] = self.load_swap_market()
        for value in markets.values():
            quote = value.get('quote', '')
            base =  value.get('base', '')
            if value.get('swap', False) and quote in self.get_allowed_quotes() and value.get('active', False) and base not in self.get_exclude_base():
                    symbols.append(value['symbol'])
        return symbols

    @abstractmethod
    def get_swap_exchange(self) -> Exchange:
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