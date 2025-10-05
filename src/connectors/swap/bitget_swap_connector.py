import ccxt
from ccxt import Exchange
from ccxt.base.types import OrderBook, Ticker

from src.connectors.data.base_ticker_info import BaseTickerInfo
from src.connectors.swap.swap_common_connector import SwapCommonConnector


class BitgetSwapConnector(SwapCommonConnector):

    def __init__(self):
        super().__init__()
        self.exchange = ccxt.bitget({'options': {'defaultType': 'mix'}})

    def fetch_order_book(self, symbol: str) -> OrderBook:
        order_book: OrderBook = self.get_exchange().fetch_order_book(symbol=symbol, limit=50)
        return order_book

    def fetch_ticker(self, symbol: str) -> BaseTickerInfo:
        ticker: Ticker = self.get_exchange().fetch_ticker(symbol=symbol)
        return self.convert_to_ticker_info(ticker, False, True, False)

    def fetch_tickers(self) -> list[BaseTickerInfo]:
        try:
            symbols = self.load_symbols()
            tickers: dict[str, Ticker] = self.get_exchange().fetch_tickers(symbols=symbols)
            return [
                self.convert_to_ticker_info(ticker, False, True, False)
                for ticker in tickers.values()
            ]
        except Exception as e:
            self.logger.log_error(f"Error during fetch tickers: {e}")
            return []

    def get_exchange(self) -> Exchange:
        return self.exchange

    def get_exchange_name(self) -> str:
        return "BITGET"