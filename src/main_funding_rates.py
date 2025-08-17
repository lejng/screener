from ccxt.base.types import FundingRate

from src.connectors.bybit_connector import BybitConnector
from src.connectors.gate_connector import GateConnector


def print_rates(exchange_name: str, rates: dict[str, list[FundingRate]]):
    print(f"======== Funding rates for exchange {exchange_name} ============")
    print("     === MAX ===")
    for rate in rates['max']:
        print(f"        {rate['symbol']}: {rate['fundingRate']}")
    print("     === MIN ===")
    for rate in rates['small']:
        print(f"        {rate['symbol']}: {rate['fundingRate']}")


if __name__ == "__main__":
    connectors = [
        BybitConnector(),
        GateConnector(),
        #MexcConnector()
    ]
    for connector in connectors:
        rates = connector.fetch_sorted_funding_rates()
        print_rates(connector.get_exchange_name(), rates)