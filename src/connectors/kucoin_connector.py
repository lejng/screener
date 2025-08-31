import ccxt
from ccxt import Exchange

from src.connectors.common_connector import CommonConnector, FundingRateInfo


class KucoinConnector(CommonConnector):

    def __init__(self):
        super().__init__()
        self.spot_exchange = ccxt.kucoin({'options': {'defaultType': 'spot'}})
        self.swap_exchange = ccxt.kucoinfutures({'options': {'defaultType': 'swap'}})
        self.future_exchange = ccxt.kucoinfutures()
        self.set_exclude_base({
            "FORM",
            "ACE",
            "DOT3S",
            "ARB3S",
            "AAVE3S",
            "BTC3L",
            "ETH3L", "ATOM3L", "LTC3S", "ATOM3S", "LTC3L", "BNB3L", "XRP3L", "SOL3S", "DOGE3L",
            "SUSHI3S", "SUSHI3L", "BTC3S", "DOT3L", "BNB3S", "LINK3S", "ADA3S", "DOGE3S", "AVAX3S",
            "NEAR3S", "XRP3S", "BCH3S", "ADA3L", "UNI3S", "ETH3S", "LINK3L", "SUI3L", "APE3L", "SOL3L",
            "AVAX3L", "ARB3L", "VET3S", "BCH3L", "AAVE3L", "SUI3S", "UNI3L", "VET3L", "APE3S", "BROCCOLI",
            "BLOCK","LAYER","TST", "ARC"
        })

    def fetch_funding_rates(self) -> list[FundingRateInfo]:
        symbols = self.load_swap_symbols()
        result = []
        for symbol in symbols:
            result.append(self.fetch_funding_rate(symbol))
        return result

    def get_swap_exchange(self) -> Exchange:
        return self.swap_exchange

    def get_spot_exchange(self) -> Exchange:
        return self.spot_exchange

    def get_future_exchange(self) -> Exchange:
        return self.future_exchange

    def get_exchange_name(self) -> str:
        return "KUCOIN"