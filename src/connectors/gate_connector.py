import ccxt
from ccxt import Exchange

from src.connectors.common_connector import CommonConnector


class GateConnector(CommonConnector):

    def __init__(self):
        super().__init__()
        self.spot_exchange = ccxt.gate({'options': {'defaultType': 'spot'}})
        self.swap_exchange = ccxt.gate({'options': {'defaultType': 'swap'}})
        self.set_exclude_base({
            "BDT", "ZERO", "CULT", "BLOCK","REAL","NEIRO","WOLF","TRC","FIRE","QI","BEAM","GST","TAP",
            "AIX","TST","DOMI","WXT","SOLS","GMRT","MTS","CAW","JAM","PIG","PIT","QUBIC","CAD"
        })

    def get_swap_exchange(self) -> Exchange:
        return self.swap_exchange

    def get_spot_exchange(self) -> Exchange:
        return self.spot_exchange

    def get_exchange_name(self) -> str:
        return "GATE"