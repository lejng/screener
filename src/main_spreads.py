from ccxt.static_dependencies.toolz.functoolz import return_none

from src.arbitrage.arbitrage_founder import ArbitrageFounder, SpreadData
from src.connectors.binance_connector import BinanceConnector
from src.connectors.bybit_connector import BybitConnector
from src.connectors.common_connector import CommonConnector, TickerInfo
from src.connectors.gate_connector import GateConnector
from src.connectors.kucoin_connector import KucoinConnector
from src.connectors.mexc_connector import MexcConnector
from src.connectors.ticker_fetcher import TickerFetcher

def get_ticker_info(ticker: TickerInfo):
    type_info=ticker.get_market_type()
    return f"{ticker.get_trading_view_name()}:{ticker.get_symbol()}:{type_info}"

def print_spread(spread: SpreadData):
    buy = spread.ticker_to_buy
    sell = spread.ticker_to_sell
    print(f"{spread.base_currency} : {spread.spread_percent} buy: [{buy.get_trading_view_name()}|{buy.get_buy_price()}], sell: [{sell.get_trading_view_name()}|{sell.get_sell_price()}]")

if __name__ == "__main__":
    connectors: list[CommonConnector] = [
        BybitConnector(),
        GateConnector(),
        MexcConnector(),
        BinanceConnector(),
        KucoinConnector()
    ]
    ticker_fetcher = TickerFetcher()
    tickers: dict[str, list[TickerInfo]] = ticker_fetcher.fetch_tickers_in_parallel(connectors, connectors, connectors)
    founder = ArbitrageFounder()
    spreads: list[SpreadData] = founder.find_arbitrage(tickers)
    for spread_info in spreads:
        print_spread(spread_info)

