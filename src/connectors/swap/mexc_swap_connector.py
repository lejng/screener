import ccxt
from ccxt import Exchange

from src.connectors.data.funding_rate_info import FundingRateInfo
from src.connectors.swap.swap_common_connector import SwapCommonConnector


class MexcSwapConnector(SwapCommonConnector):

    def __init__(self):
        super().__init__()
        self.exchange = ccxt.mexc({'options': {'defaultType': 'swap'}})

    def fetch_funding_rates(self) -> list[FundingRateInfo]:
        symbols = self.load_symbols()
        result = []
        for symbol in symbols:
            result.append(self.fetch_funding_rate(symbol))
        return result

    def get_exchange(self) -> Exchange:
        return self.exchange

    def get_exchange_name(self) -> str:
        return "MEXC"