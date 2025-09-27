import ccxt
from ccxt import Exchange

from src.connectors.swap.swap_common_connector import SwapCommonConnector


class GateSwapConnector(SwapCommonConnector):

    def __init__(self):
        super().__init__()
        self.exchange = ccxt.gate({'options': {'defaultType': 'swap'}})

    def get_exchange(self) -> Exchange:
        return self.exchange

    def get_exchange_name(self) -> str:
        return "GATEIO"