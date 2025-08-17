import ccxt
from ccxt import Exchange
from ccxt.base.types import FundingRate

from src.connectors.common_connector import CommonConnector


class MexcConnector(CommonConnector):

    def __init__(self):
        super().__init__()
        self.spot_exchange = ccxt.mexc({'options': {'defaultType': 'spot'}})
        self.swap_exchange = ccxt.mexc({'options': {'defaultType': 'swap'}})
        self.set_exclude_base({
            "TROLL","MAGA","GAME","PALM","X","PBX","AIT","TRUMP","ACP","WOLF","NEIRO","ALT",
            "ARC","BEAM","DEFI","CAW","DAOLITY","POLC","JAM","PIG","PIT","QUBIC","CAD"
        })

    def fetch_funding_rates(self) -> dict[str, FundingRate]:
        symbols = self.load_swap_symbols()
        result = {}
        for symbol in symbols:
            result[symbol] = self.get_swap_exchange().fetch_funding_rate(symbol)
        return result

    def get_swap_exchange(self) -> Exchange:
        return self.swap_exchange

    def get_spot_exchange(self) -> Exchange:
        return self.spot_exchange

    def get_exchange_name(self) -> str:
        return "MEXC"