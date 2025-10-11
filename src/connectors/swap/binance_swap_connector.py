import ccxt
from ccxt import Exchange
from ccxt.base.types import OrderBook

from src.connectors.swap.swap_common_connector import SwapCommonConnector


class BinanceSwapConnector(SwapCommonConnector):

    def __init__(self):
        super().__init__()
        self.exchange = ccxt.binanceusdm()

    def fetch_order_book(self, symbol: str) -> OrderBook:
        order_book: OrderBook = self.get_exchange().fetch_order_book(
            symbol=symbol, limit=50, params={'category': 'linear'}
        )
        return order_book

    def get_exchange(self) -> Exchange:
        return self.exchange

    def get_exchange_name(self) -> str:
        return "BINANCE"