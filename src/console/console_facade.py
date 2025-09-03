from src.arbitrage.arbitrage_founder import ArbitrageFounder
from src.arbitrage.data.spread_data import SpreadData
from src.config.common_config import CommonConfig
from src.connectors.common_connector import CommonConnector
from src.connectors.data.aggregate_ticker import AggregateTicker
from src.connectors.data.funding_rate_info import FundingRateInfo
from src.connectors.data.ticker_info import TickerInfo
from src.connectors.ticker_fetcher import TickerFetcher


def print_spreads(header: str, spreads: list[SpreadData], min_spread: float):
    print(f"======== {header} [ min spread = {min_spread}] ============")
    for spread_info in spreads:
        print_spread(spread_info)

def print_spread(spread: SpreadData):
    buy = spread.ticker_to_buy
    sell = spread.ticker_to_sell
    line = (f"{spread.base_currency} :" +
            f" {spread.spread_percent} buy:" +
            f" [{buy.get_trading_view_name()}|{buy.get_buy_price()}], sell:" +
            f" [{sell.get_trading_view_name()}|{sell.get_sell_price()}]")
    print(line)

def print_top_rates(exchange_name: str, top_rates: dict[str, list[FundingRateInfo]]):
    print(f"======== Top funding rates for exchange {exchange_name} ============")
    space = "     "
    print(f"{space}=== MAX ===")
    for rate in top_rates['max']:
        print_rate(rate, space)
    print(f"{space}=== MIN ===")
    for rate in top_rates['small']:
        print_rate(rate, space)

def print_rate(rate: FundingRateInfo, space: str):
    line = (f"{space} {rate.get_symbol()}: " +
            f"rate: {rate.get_funding_rate_percent()} % ," +
            f"interval: {rate.get_interval()} ," +
            f"action: {rate.get_action_for_collect_funding()} ")
    print(line)

class ConsoleFacade:

    def __init__(self, all_connectors: list[CommonConnector]):
        self.common_config = CommonConfig('common_settings.yaml')
        self.ticker_fetcher = TickerFetcher()
        self.founder = ArbitrageFounder()
        self.all_connectors = all_connectors

    def print_funding_rate_by_quote(self):
        base = input("Enter coin name (base currency): ")
        self.common_config.read_config()
        connectors = self.get_swap_connectors()
        for connector in connectors:
            print(f"======== Funding rates for exchange {connector.get_exchange_name()} ============")
            rates: list[FundingRateInfo] = connector.fetch_funding_rate_by_base(base)
            for rate in rates:
                print_rate(rate, "")

    def print_top_funding_rates(self):
        self.common_config.read_config()
        exchanges = self.common_config.get_exchanges_for_fetch_top_fundings()
        connectors = []
        for connector in self.all_connectors:
            if connector.get_exchange_name() in exchanges:
                connectors.append(connector)
        for connector in connectors:
            rates: dict[str, list[FundingRateInfo]] = connector.fetch_top_funding_rates()
            print_top_rates(connector.get_exchange_name(), rates)

    def print_all_spreads(self):
        spreads: list[SpreadData] = self.find_spreads()
        # remove situation where buy futures/swap and sell spot, because usually impossible open short spot position
        filtered_spreads = [
            item for item in spreads
            if not (item.ticker_to_sell.spot
                    and (item.ticker_to_buy.swap or item.ticker_to_buy.future))
        ]
        print_spreads("All arbitrage situations", filtered_spreads, self.common_config.get_min_spread())

    def print_spreads_without_transfer(self):
        spreads: list[SpreadData] = self.find_spreads()
        # remove spot-spot pairs
        filtered_spreads = [
            item for item in spreads
            if not item.ticker_to_sell.spot
        ]
        print_spreads("Arbitrage situations without SPOT-SPOT pairs", filtered_spreads, self.common_config.get_min_spread())

    def find_spreads(self) -> list[SpreadData]:
        self.common_config.reload_config()
        tickers: dict[str, list[TickerInfo]] = self.ticker_fetcher.fetch_tickers_in_parallel(
            self.get_spot_connectors(),
            self.get_swap_connectors(),
            self.get_futures_connectors()
        )
        return self.founder.find_arbitrage(tickers, self.common_config.get_min_spread())

    def get_spot_connectors(self) -> list[CommonConnector]:
        exchanges = self.common_config.get_spot_exchanges()
        result = []
        for connector in self.all_connectors:
            if connector.get_exchange_name() in exchanges:
                result.append(connector)
        return result

    def get_swap_connectors(self) -> list[CommonConnector]:
        exchanges = self.common_config.get_swap_exchanges()
        result = []
        for connector in self.all_connectors:
            if connector.get_exchange_name() in exchanges:
                result.append(connector)
        return result

    def get_futures_connectors(self) -> list[CommonConnector]:
        exchanges = self.common_config.get_futures_exchanges()
        result = []
        for connector in self.all_connectors:
            if connector.get_exchange_name() in exchanges:
                result.append(connector)
        return result

    def print_volume_weighted_average_price(self):
        self.common_config.reload_config()
        base = input("Enter coin name: ")
        amount_in_quote = self.common_config.get_amount_in_quote()
        tickers: list[AggregateTicker] = self.ticker_fetcher.fetch_tickers_by_base(
            self.get_spot_connectors(),
            self.get_swap_connectors(),
            self.get_futures_connectors(),
            base
        )
        for ticker in tickers:
            ticker_info = ticker.ticker
            vwap_buy, vwap_sell = ticker.vwap_order_book(amount_in_quote)
            coins_buy = amount_in_quote / vwap_buy
            coins_sell = amount_in_quote / vwap_sell
            line = (f"{ticker_info.get_trading_view_name()}, quote amount: {amount_in_quote}"
                    f"| buy price: {vwap_buy}, coins to buy: {coins_buy}"
                    f"| sell price: {vwap_sell}, coins to sell: {coins_sell}")
            print(line)
