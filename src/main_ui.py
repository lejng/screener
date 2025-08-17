from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QHBoxLayout, QCheckBox, QProgressBar
)
import sys
from PySide6.QtCore import QThread

from src.arbitrage.arbitrage_founder import SpreadData
from src.config.custom_logger import CustomLogger
from src.connectors.bybit_connector import BybitConnector
from src.connectors.common_connector import CommonConnector
from src.connectors.gate_connector import GateConnector
from src.connectors.mexc_connector import MexcConnector
from src.ui.arbitrage_list_worker import ArbitrageListWorker

default_min_spread: str = "1"

class ArbitrageUI(QWidget):
    def __init__(self):
        super().__init__()
        self.spreads = []
        self.workers = []
        self.threads = []
        self.logger = CustomLogger()
        self.setWindowTitle("Arbitration screener")
        self.resize(900, 700)
        self.layout = QVBoxLayout(self)

        # create spread input form
        spread_layout = self.create_spread_layout()
        self.layout.addLayout(spread_layout)

        # create choose exchange for scan
        self.all_connectors: list[CommonConnector] = [
            BybitConnector(),
            GateConnector(),
            MexcConnector()
        ]
        self.swap_checkboxes: dict[CommonConnector, QCheckBox] = {}
        self.spot_checkboxes: dict[CommonConnector, QCheckBox] = {}
        self.layout.addLayout(self.create_exchange_checkbox_group("Swap Exchanges", self.swap_checkboxes))
        self.layout.addLayout(self.create_exchange_checkbox_group("Spot Exchanges", self.spot_checkboxes))

        # create find button
        self.button = QPushButton("Find")
        self.button.clicked.connect(self.start_finding_arbitrage)

        # create loading bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # marquee
        self.progress.hide()
        self.layout.addWidget(self.progress)

        # create table spreads
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Base currency", "Ticker to buy", "Buy price", "Ticker to sell", "Sell price", "Spread", "More info"])
        #self.table.cellClicked.connect(self.on_pair_clicked)

        self.layout.addWidget(self.button)
        self.layout.addWidget(self.table)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def create_spread_layout(self) -> QHBoxLayout:
        filter_layout = QHBoxLayout()
        self.min_spread_input = QLineEdit()
        self.min_spread_input.setPlaceholderText(default_min_spread)
        filter_layout.addWidget(QLabel("Min spread (%):"))
        filter_layout.addWidget(self.min_spread_input)
        return filter_layout

    def get_min_spread(self) -> float:
        try:
            return float(self.min_spread_input.text() or default_min_spread)
        except ValueError:
            return 0.0

    def create_exchange_checkbox_group(self, title: str, checkbox_dict:  dict[CommonConnector, QCheckBox]) -> QHBoxLayout:
        group_layout = QHBoxLayout()
        group_label = QLabel(title)
        group_layout.addWidget(group_label)

        for connector in self.all_connectors:
            checkbox = QCheckBox(connector.get_exchange_name())
            checkbox.setChecked(True)
            checkbox_dict[connector] = checkbox
            group_layout.addWidget(checkbox)

        return group_layout

    def get_swap_exchanges(self) -> list[CommonConnector]:
        return [exchange for exchange, checkbox in self.swap_checkboxes.items() if checkbox.isChecked()]

    def get_spot_exchanges(self) -> list[CommonConnector]:
        return [exchange for exchange, checkbox in self.spot_checkboxes.items() if checkbox.isChecked()]

    def start_finding_arbitrage(self):
        min_spread = self.get_min_spread()
        self.progress.show()
        self.button.setEnabled(False)
        # Создаём поток и воркер
        worker = ArbitrageListWorker(min_spread, self.get_swap_exchanges(), self.get_spot_exchanges())
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
            if not (item.ticker_to_sell.spot
                    and item.ticker_to_buy.swap)
        ]
        self.table.setRowCount(len(self.spreads))
        for index, spread in enumerate(self.spreads):
            self.table.setItem(index, 0, QTableWidgetItem(spread.base_currency))
            self.table.setItem(index, 1, QTableWidgetItem(spread.ticker_to_buy.get_trading_view_name()))
            self.table.setItem(index, 2, QTableWidgetItem(spread.ticker_to_buy.get_buy_price().__str__()))
            self.table.setItem(index, 3, QTableWidgetItem(spread.ticker_to_sell.get_trading_view_name()))
            self.table.setItem(index, 4, QTableWidgetItem(spread.ticker_to_sell.get_sell_price().__str__()))
            self.table.setItem(index, 5, QTableWidgetItem(spread.spread_percent.__str__()))
            self.table.setItem(index, 6, QTableWidgetItem("Open"))

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.progress.hide()
        self.button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArbitrageUI()
    window.show()
    sys.exit(app.exec())