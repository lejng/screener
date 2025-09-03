import ccxt
from ccxt import Exchange

from src.connectors.common_connector import CommonConnector
from src.connectors.data.funding_rate_info import FundingRateInfo
from src.connectors.data.ticker_info import TickerInfo


class MexcConnector(CommonConnector):

    def __init__(self):
        super().__init__()
        self.spot_exchange = ccxt.mexc({'options': {'defaultType': 'spot'}})
        self.swap_exchange = ccxt.mexc({'options': {'defaultType': 'swap'}})
        self.set_exclude_base({
            "TROLL","MAGA","GAME","PALM","X","PBX","AIT","TRUMP","ACP","WOLF","NEIRO","ALT",
            "ARC","BEAM","DEFI","CAW","DAOLITY","POLC","JAM","PIG","PIT","QUBIC","CAD"
        })

    def fetch_funding_rates(self) -> list[FundingRateInfo]:
        symbols = self.load_swap_symbols()
        result = []
        for symbol in symbols:
            result.append(self.fetch_funding_rate(symbol))
        return result

    def fetch_future_tickers(self) -> list[TickerInfo]:
        return []

    def get_swap_exchange(self) -> Exchange:
        return self.swap_exchange

    def get_spot_exchange(self) -> Exchange:
        return self.spot_exchange

    def get_future_exchange(self) -> Exchange:
        return self.spot_exchange

    def get_exchange_name(self) -> str:
        return "MEXC"