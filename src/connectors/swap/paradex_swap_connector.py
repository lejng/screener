from typing import Optional

import ccxt
from ccxt import Exchange
from ccxt.base.types import MarketInterface

from src.connectors.data.funding_rate_info import FundingRateInfo
from src.connectors.swap.swap_common_connector import SwapCommonConnector


class ParadexSwapConnector(SwapCommonConnector):

    def __init__(self):
        super().__init__()
        self.exchange = ccxt.paradex()

    def fetch_funding_rate(self, symbol: str) -> Optional[FundingRateInfo]:
        # ccxt lib do not support fetch funding for paradex exchange
        return None

    def load_symbols_by_base(self, base: str) -> list[str]:
        symbols = []
        markets: dict[str, MarketInterface] = self.get_exchange().load_markets()
        for value in markets.values():
            quote = value.get('settle', '')
            base_value = value.get('base', '')
            if (base_value.lower() == base.lower()
                    and value.get('swap', False)
                    and quote in self.get_allowed_quotes()):
                symbols.append(value['symbol'])
        return symbols

    def load_symbols(self) -> list[str]:
        symbols = []
        markets: dict[str, MarketInterface] = self.get_exchange().load_markets()
        for value in markets.values():
            quote = value.get('settle', '')
            base =  value.get('base', '')
            if (value.get('swap', False)
                    and quote in self.get_allowed_quotes()
                    and base not in self.get_exclude_base()):
                    symbols.append(value['symbol'])
        return symbols

    def get_exchange(self) -> Exchange:
        return self.exchange

    def get_exchange_name(self) -> str:
        return "PARADEX"