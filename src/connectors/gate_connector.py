import ccxt
from ccxt import Exchange
from ccxt.base.types import Ticker

from src.connectors.common_connector import CommonConnector, TickerInfo


class GateConnector(CommonConnector):

    def __init__(self):
        super().__init__()
        self.spot_exchange = ccxt.gate({'options': {'defaultType': 'spot'}})
        self.swap_exchange = ccxt.gate({'options': {'defaultType': 'swap'}})
        self.future_exchange = ccxt.gate()
        self.set_exclude_base({
            "BDT", "ZERO", "CULT", "BLOCK","REAL","NEIRO","WOLF","TRC","FIRE","QI","BEAM","GST","TAP",
            "AIX","TST","DOMI","WXT","SOLS","GMRT","MTS","CAW","JAM","PIG","PIT","QUBIC","CAD","CLV"
        })

    def fetch_future_tickers(self) -> list[TickerInfo]:
        symbols = self.load_future_symbols()
        tickers: list[TickerInfo] = []
        for symbol in symbols:
            ticker: Ticker = self.get_future_exchange().fetch_ticker(symbol=symbol)
            tickers.append(self.convert_to_ticker_info(ticker, False, False, True))
        return tickers

    def get_swap_exchange(self) -> Exchange:
        return self.swap_exchange

    def get_spot_exchange(self) -> Exchange:
        return self.spot_exchange

    def get_future_exchange(self) -> Exchange:
        return self.future_exchange

    def get_exchange_name(self) -> str:
        return "GATEIO"