from PySide6.QtCore import QObject, Signal

from src.arbitrage.arbitrage_founder import ArbitrageFounder
from src.arbitrage.data.spread_data import SpreadData
from src.connectors.common_connector import CommonConnector
from src.connectors.data.base_ticker_info import BaseTickerInfo
from src.connectors.ticker_fetcher import TickerFetcher


class ArbitrageListWorker(QObject):
    finished = Signal(list)

    def __init__(self, min_spread: float, spot_connectors: list[CommonConnector], swap_connectors: list[CommonConnector]):
        super().__init__()
        self.min_spread = min_spread
        self.arbitrage_founder = ArbitrageFounder()
        self.swap_connectors = swap_connectors
        self.spot_connectors = spot_connectors
        self.ticker_fetcher = TickerFetcher()

    def run(self):
        tickers: dict[str, list[BaseTickerInfo]] = self.ticker_fetcher.fetch_tickers_in_parallel(self.spot_connectors, self.swap_connectors, [])
        spreads: list[SpreadData] = self.arbitrage_founder.find_arbitrage(tickers, self.min_spread)
        self.finished.emit(spreads)