from PySide6.QtCore import QObject, Signal

from src.arbitrage.arbitrage_founder import ArbitrageFounder, SpreadData
from src.connectors.common import ExchangeName


class ArbitrageListWorker(QObject):
    finished = Signal(list)

    def __init__(self, min_spread: float, arbitrage_founder: ArbitrageFounder,
                 swap_exchanges: list[ExchangeName], spot_exchanges: list[ExchangeName]):
        super().__init__()
        self.min_spread = min_spread
        self.arbitrage_founder = arbitrage_founder
        self.swap_exchanges = swap_exchanges
        self.spot_exchanges = spot_exchanges

    def run(self):
        spreads: list[SpreadData] = self.arbitrage_founder.find_arbitrage(
            self.swap_exchanges,
            self.spot_exchanges,
            self.min_spread
        )
        self.finished.emit(spreads)