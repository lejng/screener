import ccxt
from ccxt import Exchange

from src.connectors.spot.spot_common_connector import SpotCommonConnector


class BybitSpotConnector(SpotCommonConnector):

    def __init__(self):
        super().__init__()
        self.exchange = ccxt.bybit({'options': {'defaultType': 'spot'}})

    def get_exchange(self) -> Exchange:
        return self.exchange

    def get_exchange_name(self) -> str:
        return "BYBIT"