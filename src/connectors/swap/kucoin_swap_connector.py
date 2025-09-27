import ccxt
from ccxt import Exchange
from ccxt.base.types import OrderBook

from src.connectors.data.funding_rate_info import FundingRateInfo
from src.connectors.swap.swap_common_connector import SwapCommonConnector


class KucoinSwapConnector(SwapCommonConnector):

    def __init__(self):
        super().__init__()
        self.exchange = ccxt.kucoinfutures({'options': {'defaultType': 'swap'}})

    def fetch_funding_rates(self) -> list[FundingRateInfo]:
        symbols = self.load_symbols()
        result = []
        for symbol in symbols:
            result.append(self.fetch_funding_rate(symbol))
        return result

    def fetch_order_book(self, symbol: str) -> OrderBook:
        order_book: OrderBook = self.get_exchange().fetch_order_book(symbol=symbol, limit=100, params={'category': 'swap'})
        return order_book

    def get_exchange(self) -> Exchange:
        return self.exchange

    def get_exchange_name(self) -> str:
        return "KUCOIN"