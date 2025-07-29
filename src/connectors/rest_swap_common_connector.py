import re

import ccxt
from ccxt import Exchange
from ccxt.base.types import Ticker

from src.config.custom_logger import CustomLogger
from src.connectors.common import ExchangeName, TickerData, MarketType, convert_ticker


class RestSwapCommonConnector:
    def __init__(self, allowed_quotes: set[str], exclude_base: set[str]):
        self.logger = CustomLogger()
        self.allowed_quotes = allowed_quotes
        self.exclude_base= exclude_base
        options_swap = {'defaultType': 'swap'}
        self.exchanges: dict[ExchangeName, Exchange] = {
            ExchangeName.BYBIT: ccxt.bybit({'options': options_swap}),
            ExchangeName.MEXC: ccxt.mexc({'options': options_swap}),
            ExchangeName.GATE: ccxt.gate({'options': options_swap}),
            ExchangeName.KRAKEN: ccxt.krakenfutures({'options': options_swap})
        }

    def fetch_swap_by_exchange(self, exchange_name: ExchangeName) -> dict[str, list[TickerData]]:
        if exchange_name is ExchangeName.BYBIT:
            return self.fetch_bybit()
        if exchange_name is ExchangeName.MEXC:
            return self.fetch_mexc()
        if exchange_name is ExchangeName.KRAKEN:
            return self.fetch_kraken()
        if exchange_name is ExchangeName.GATE:
            return self.fetch_gate()
        self.logger.log_info(f"Can not fetch tickers for exchange with name: {exchange_name}")
        return {}

    def fetch_bybit(self) -> dict[str, list[TickerData]]:
        return self.fetch_swap(ExchangeName.BYBIT, {'category': 'linear'})

    def fetch_gate(self) -> dict[str, list[TickerData]]:
        return self.fetch_swap(ExchangeName.GATE, {'type': 'swap'})

    def fetch_mexc(self) -> dict[str, list[TickerData]]:
        return self.fetch_swap(ExchangeName.MEXC,{'type': 'swap'})

    def fetch_kraken(self) -> dict[str, list[TickerData]]:
        tickers: dict[str, list[TickerData]] = self.fetch_swap(ExchangeName.KRAKEN, {'type': 'swap'})
        for key, values in tickers.items():
            # Фильтруем список, оставляя только НЕ фьючерсы с экспирацией
            filtered_values = [
                element for element in values
                if not self.is_expirable_future(element.exchange_id)
            ]
            tickers[key] = filtered_values  # Заменяем старый список на отфильтрованный
        return tickers

    def is_expirable_future(self, symbol: str) -> bool:
        """Проверяет, является ли символ фьючерсом с датой экспирации (напр., -250926)."""
        pattern = r"-\d{6}$"  # "$" означает "конец строки"
        return bool(re.search(pattern, symbol))

    def fetch_swap(self, name: ExchangeName, params) -> dict[str, list[TickerData]]:
        symbols = self.load_swap_symbols(name)
        tickers: dict[str, Ticker] = self.exchanges[name].fetch_tickers(symbols=symbols, params=params)  # spot,linear,inverse,option
        return convert_ticker(tickers, name, MarketType.SWAP)

    def load_swap_symbols(self, exchange_name: ExchangeName) -> list[str]:
        symbols = []
        markets = self.exchanges[exchange_name].load_markets()
        for value in markets.values():
            quote = value.get('quote', '')
            base = value.get('base', '')
            if value.get('swap', False) and quote in self.allowed_quotes and value.get('active', False) and base not in self.exclude_base:
                symbols.append(value['symbol'])
        return symbols
