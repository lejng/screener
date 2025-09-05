from typing import Optional

from src.arbitrage.arbitrage_founder import ArbitrageFounder
from src.arbitrage.data.spread_data import SpreadData
from src.config.common_config import CommonConfig
from src.connectors.common_connector import CommonConnector
from src.connectors.data.full_ticker_info import FullTickerInfo
from src.connectors.data.funding_rate_info import FundingRateInfo
from src.connectors.data.base_ticker_info import BaseTickerInfo
from src.connectors.ticker_fetcher import TickerFetcher


# ============= Print full spread data (checking order book and funding) =============
def print_full_spreads_data(spreads: list[SpreadData]):
    for spread in spreads:
        buy = spread.ticker_to_buy
        sell = spread.ticker_to_sell
        buy_funding = get_funding_line(buy.get_funding_info())
        sell_funding = get_funding_line(sell.get_funding_info())
        funding_spread_adjustment = spread.get_funding_spread_adjustment()
        final_spread = spread.spread_percent + funding_spread_adjustment
        line = (f"{spread.base_currency} :" +
                f" spread: {spread.spread_percent} " +
                f" spread with funding adjustment: {final_spread} buy:" +
                f" [{buy.get_trading_view_name()} | price: {buy.get_best_buy_price()} | coins: {buy.get_coins_to_buy()}{buy_funding}], sell:" +
                f" [{sell.get_trading_view_name()} | price: {sell.get_best_sell_price()} | coins: {sell.get_coins_to_sell()}{sell_funding}]")
        print(line)

def get_funding_line(rate: Optional[FundingRateInfo]):
    if rate:
        return (
                f"| funding rate: {rate.get_funding_rate_percent()} % ," +
                f"interval: {rate.get_interval()} ," +
                f"action: {rate.get_action_for_collect_funding()} "
        )
    return ""


# ============= Print spreads data (quick search, without order book and funding) =============
def print_spreads(header: str, spreads: list[SpreadData], min_spread: float):
    print(f"======== {header} [ min spread = {min_spread}] ============")
    for spread_info in spreads:
        print_spread(spread_info)

def print_spread(spread: SpreadData):
    buy = spread.ticker_to_buy
    sell = spread.ticker_to_sell
    line = (f"{spread.base_currency} :" +
            f" {spread.spread_percent} buy:" +
            f" [{buy.get_trading_view_name()}|{buy.get_best_buy_price()}], sell:" +
            f" [{sell.get_trading_view_name()}|{sell.get_best_sell_price()}]")
    print(line)

# ============= Print funding =============
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

# ============= Utils methods =============
# remove situation where buy futures/swap and sell spot, because usually impossible open short spot position
def filter_wrong_pairs(spreads: list[SpreadData]) -> list[SpreadData]:
     return [
        item for item in spreads
        if not (item.ticker_to_sell.spot
                and (item.ticker_to_buy.swap or item.ticker_to_buy.future))
    ]

class ConsoleFacade:

    def __init__(self, all_connectors: list[CommonConnector]):
        self.common_config = CommonConfig('common_settings.yaml')
        self.ticker_fetcher = TickerFetcher()
        self.founder = ArbitrageFounder()
        self.all_connectors = all_connectors

    def print_funding_rate_for_coin(self):
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
        filtered_spreads = filter_wrong_pairs(spreads)
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
        tickers: dict[str, list[BaseTickerInfo]] = self.ticker_fetcher.fetch_tickers_in_parallel(
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

    def print_spread_for_coin(self):
        self.common_config.reload_config()
        base = input("Enter coin name: ")
        amount_in_quote = self.common_config.get_amount_in_quote()
        tickers: list[FullTickerInfo] = self.ticker_fetcher.fetch_tickers_by_base(
            self.get_spot_connectors(),
            self.get_swap_connectors(),
            self.get_futures_connectors(),
            base,
            amount_in_quote
        )
        spreads :list[SpreadData] = self.founder.calculate_spreads(tickers, 0.1, base)
        filtered_spreads = filter_wrong_pairs(spreads)
        print_full_spreads_data(filtered_spreads)
