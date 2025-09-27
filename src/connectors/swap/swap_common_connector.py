from abc import abstractmethod
from typing import Optional

from ccxt import Exchange
from ccxt.base.types import MarketInterface, Ticker, OrderBook, FundingRate

from src.connectors.common_connector import CommonConnector
from src.connectors.data.base_ticker_info import BaseTickerInfo
from src.connectors.data.funding_rate_info import FundingRateInfo


class SwapCommonConnector(CommonConnector):

    def __init__(self):
        super().__init__()

    def fetch_top_funding_rates(self, max_count = 10) -> dict[str, list[FundingRateInfo]] :
        rates: list[FundingRateInfo] = self.fetch_funding_rates()
        top_max = sorted(rates, key=lambda x: x.get_funding_rate(), reverse=True)[:max_count]
        top_small = sorted(rates, key=lambda x: x.get_funding_rate(), reverse=False)[:max_count]
        return {'max': top_max, 'small': top_small}

    def fetch_funding_rates(self) -> list[FundingRateInfo]:
        symbols = self.load_symbols()
        rates: dict[str, FundingRate] = self.get_exchange().fetch_funding_rates(symbols=symbols)
        return [
            FundingRateInfo(rate)
            for rate in rates.values()
        ]

    def fetch_funding_rate(self, symbol: str) -> Optional[FundingRateInfo]:
        rate: FundingRate = self.get_exchange().fetch_funding_rate(symbol)
        return FundingRateInfo(rate)

    def fetch_order_book(self, symbol: str) -> OrderBook:
        order_book: OrderBook = self.get_exchange().fetch_order_book(symbol=symbol, limit=50, params={'category': 'swap'})
        return order_book

    def fetch_ticker(self, symbol: str) -> BaseTickerInfo:
        ticker: Ticker = self.get_exchange().fetch_ticker(symbol=symbol, params={'category': 'swap'})
        return self.convert_to_ticker_info(ticker, False, True, False)

    def fetch_tickers(self) -> list[BaseTickerInfo]:
        symbols = self.load_symbols()
        tickers: dict[str, Ticker] = self.get_exchange().fetch_tickers(symbols=symbols, params={'category': 'swap'})
        return [
            self.convert_to_ticker_info(ticker, False, True, False)
            for ticker in tickers.values()
        ]

    def load_symbols(self) -> list[str]:
        symbols = []
        markets: dict[str, MarketInterface] = self.get_exchange().load_markets()
        for value in markets.values():
            quote = value.get('quote', '')
            base =  value.get('base', '')
            if (value.get('swap', False)
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
                    and value.get('swap', False)
                    and value.get('active', False)
                    and quote in self.get_allowed_quotes()):
                symbols.append(value['symbol'])
        return symbols

    @abstractmethod
    def get_exchange(self) -> Exchange:
        pass

    @abstractmethod
    def get_exchange_name(self) -> str:
        pass