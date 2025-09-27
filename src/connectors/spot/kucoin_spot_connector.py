import ccxt
from ccxt import Exchange
from ccxt.base.types import OrderBook

from src.connectors.spot.spot_common_connector import SpotCommonConnector


class KucoinSpotConnector(SpotCommonConnector):

    def __init__(self):
        super().__init__()
        self.exchange = ccxt.kucoin({'options': {'defaultType': 'spot'}})

    def fetch_order_book(self, symbol: str) -> OrderBook:
        order_book: OrderBook = self.get_exchange().fetch_order_book(symbol=symbol, limit=100, params={'type': 'spot'})
        return order_book

    def get_exchange(self) -> Exchange:
        return self.exchange

    def get_exchange_name(self) -> str:
        return "KUCOIN"