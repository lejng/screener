import ccxt
from ccxt import Exchange
from ccxt.base.types import Ticker

from src.config.custom_logger import CustomLogger
from src.connectors.common import ExchangeName, TickerData, convert_ticker, MarketType


class RestSpotCommonConnector:
    def __init__(self, allowed_quotes: set[str], exclude_base: set[str]):
        self.logger = CustomLogger()
        self.allowed_quotes = allowed_quotes
        self.exclude_base = exclude_base
        options_spot = {'options': {'defaultType': 'spot'}}
        self.exchanges: dict[ExchangeName, Exchange] = {
            ExchangeName.BYBIT: ccxt.bybit({'options': options_spot}),
            ExchangeName.MEXC: ccxt.mexc({'options': options_spot}),
            ExchangeName.GATE: ccxt.gate({'options': options_spot}),
            ExchangeName.KRAKEN: ccxt.kraken({'options': options_spot}),
        }

    def fetch_spot_by_exchange(self, exchange_name: ExchangeName) -> dict[str, list[TickerData]]:
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

    def fetch_gate(self) -> dict[str, list[TickerData]]:
        return self.fetch_spot(ExchangeName.GATE, {'type': 'spot'})

    def fetch_mexc(self) -> dict[str, list[TickerData]]:
        return self.fetch_spot(ExchangeName.MEXC, {'type': 'spot'})

    def fetch_bybit(self) -> dict[str, list[TickerData]]:
        return self.fetch_spot(ExchangeName.BYBIT, {'type': 'spot'})

    def fetch_kraken(self) -> dict[str, list[TickerData]]:
        return self.fetch_spot(ExchangeName.KRAKEN, {'type': 'spot'})

    def fetch_spot(self, name: ExchangeName, params) -> dict[str, list[TickerData]]:
        symbols = self.load_spot_symbols(name)
        tickers: dict[str, Ticker] = self.exchanges[name].fetch_tickers(symbols=symbols, params=params)  # spot,linear,inverse,option
        return convert_ticker(tickers, name, MarketType.SPOT)

    def load_spot_symbols(self, exchange_name: ExchangeName) -> list[str]:
        symbols = []
        markets = self.exchanges[exchange_name].load_markets()
        for value in markets.values():
            quote = value.get('quote', '')
            base =  value.get('base', '')
            if value.get('spot', False) and quote in self.allowed_quotes and value.get('active', False) and base not in self.exclude_base:
                    symbols.append(value['symbol'])
        return symbols
