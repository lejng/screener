from src.arbitrage.arbitrage_founder import ArbitrageFounder, SpreadData

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QHBoxLayout
)
import sys
from PySide6.QtCore import QThread

from src.config.custom_logger import CustomLogger
from src.connectors.common import ExchangeName, MarketType
from src.ui.arbitrage_list_worker import ArbitrageListWorker

allowed_quotes = {'USDT', 'USDC', 'USDE'}
exclude_base = {
    'BDT', 'TRUMP', 'MAGA', 'TAP', 'ZERO', 'CULT', 'PALM', 'WELL', 'BLOCK', 'REAL', 'WX', 'PBX', 'NEIRO', 'AIT', 'ACP', 'TST', 'FIRE', 'WOLF', 'TRC', 'ALT', 'SOLS', 'BEAM', 'JAM',
    'CAW','GAME','AIX','CAD','DOMI','NAWS','OXY','ARC','QI','PTC','GO','AIR','BSX','WXT','MTS','GST','URO','FMC','SNS','GMRT','HRT','DEFI','POLC','CLV','WHITE','DESCI','BBQ',
    'DELABS','PUNDIAI','MAN','CLAY','KITEAI','PIT','PIG','CANTO','CERE'
}

class ArbitrageUI(QWidget):
    def __init__(self):
        super().__init__()
        self.spreads = []
        self.workers = []
        self.threads = []
        self.logger = CustomLogger()
        self.arbitrage_founder = ArbitrageFounder(self.get_allowed_quotes(), self.get_exclude_base())
        self.setWindowTitle("Arbitration screener")
        self.resize(900, 700)
        self.layout = QVBoxLayout(self)

        # create spread input form
        spread_layout = self.create_spread_layout()
        self.layout.addLayout(spread_layout)

        # create find button
        self.button = QPushButton("Find")
        self.button.clicked.connect(self.start_finding_arbitrage)

        # create loading label
        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)

        # create table spreads
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Base currency", "Buy", "Sell", "Spread", "Current spread (click for update)"])
        #self.table.cellClicked.connect(self.on_pair_clicked)

        self.layout.addWidget(self.button)
        self.layout.addWidget(self.table)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def create_spread_layout(self) -> QHBoxLayout:
        filter_layout = QHBoxLayout()
        self.min_spread_input = QLineEdit()
        self.min_spread_input.setPlaceholderText("0.7")
        filter_layout.addWidget(QLabel("Min spread (%):"))
        filter_layout.addWidget(self.min_spread_input)
        return filter_layout

    def get_min_spread(self) -> float:
        try:
            return float(self.min_spread_input.text() or "0.7")
        except ValueError:
            return 0.0

    def get_allowed_quotes(self):
        # we can implement it take from ui side
        return allowed_quotes

    def get_exclude_base(self):
        # we can implement it take from ui side
        return exclude_base

    def get_swap_exchanges(self) -> list[ExchangeName]:
        # we can add field for check or uncheck exchanges
        # [ExchangeName.KRAKEN, ExchangeName.BYBIT, ExchangeName.GATE, ExchangeName.MEXC]
        return [ExchangeName.BYBIT, ExchangeName.GATE]

    def get_spot_exchanges(self) -> list[ExchangeName]:
        # we can add field for check or uncheck exchanges
        # [ExchangeName.KRAKEN, ExchangeName.BYBIT, ExchangeName.GATE, ExchangeName.MEXC]
        return [ExchangeName.KRAKEN, ExchangeName.BYBIT, ExchangeName.GATE]

    def start_finding_arbitrage(self):
        min_spread = self.get_min_spread()
        self.status_label.setText("🔎 Scanning...")
        self.button.setEnabled(False)
        self.arbitrage_founder.update_exclude_base(self.get_exclude_base())
        self.arbitrage_founder.update_allowed_quotes(self.get_allowed_quotes())
        # Создаём поток и воркер
        worker = ArbitrageListWorker(min_spread, self.arbitrage_founder, self.get_swap_exchanges(), self.get_spot_exchanges())
        self.start_thread(worker, self.fill_arbitrage_table)

    def start_thread(self, worker, update_ui_callback):
        # Создаём поток и воркер
        thread = QThread()
        worker.moveToThread(thread)
        # Подключаем сигналы
        thread.started.connect(worker.run)
        worker.finished.connect(update_ui_callback)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.workers.append(worker)
        self.threads.append(thread)
        thread.finished.connect(lambda: self.threads.remove(thread))
        thread.finished.connect(lambda: self.workers.remove(worker))
        thread.start()


    def fill_arbitrage_table(self, spreads: list[SpreadData]):
        self.spreads = [
            item for item in spreads
            if not (item.ticker_to_sell.market_type == MarketType.SPOT
                    and item.ticker_to_buy.market_type == MarketType.SWAP)
        ]
        self.table.setRowCount(len(self.spreads))
        for index, spread in enumerate(self.spreads):
            self.table.setItem(index, 0, QTableWidgetItem(spread.base_currency))
            self.table.setItem(index, 1, QTableWidgetItem(spread.ticker_to_buy.get_trading_view_name()))
            self.table.setItem(index, 2, QTableWidgetItem(spread.ticker_to_sell.get_trading_view_name()))
            self.table.setItem(index, 3, QTableWidgetItem(spread.spread_percent.__str__()))
            self.table.setItem(index, 4, QTableWidgetItem("Click for update"))

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.status_label.setText("✅ Searching finished")
        self.button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArbitrageUI()
    window.show()
    sys.exit(app.exec())