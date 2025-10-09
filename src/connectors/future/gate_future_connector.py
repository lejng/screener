import ccxt
from ccxt import Exchange

from src.connectors.data.base_ticker_info import BaseTickerInfo
from src.connectors.future.future_common_connector import FutureCommonConnector


class GateFutureConnector(FutureCommonConnector):

    def __init__(self):
        super().__init__()
        self.exchange = ccxt.gate({'options': {'defaultType': 'future'}})

    def fetch_tickers(self) -> list[BaseTickerInfo]:
        try:
            symbols = self.load_symbols()
            tickers: list[BaseTickerInfo] = []
            for symbol in symbols:
                ticker: BaseTickerInfo = self.fetch_ticker(symbol=symbol)
                tickers.append(ticker)
            return tickers
        except Exception as e:
            self.logger.log_error(f"Error during fetch tickers: {e}")
            return []

    def get_exchange(self) -> Exchange:
        return self.exchange

    def get_exchange_name(self) -> str:
        return "GATEIO"