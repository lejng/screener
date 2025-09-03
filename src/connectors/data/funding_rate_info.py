from dataclasses import dataclass

from ccxt.base.types import FundingRate


@dataclass
class FundingRateInfo:
    funding_rate: FundingRate

    def get_funding_rate(self) -> float:
        return self.funding_rate['fundingRate']

    def get_funding_rate_percent(self) -> float:
        return self.funding_rate['fundingRate'] * 100

    def get_symbol(self) -> str:
        return self.funding_rate['symbol']

    def get_interval(self) -> str:
        return self.funding_rate["interval"]

    def get_action_for_collect_funding(self) -> str:
        if self.funding_rate['fundingRate'] > 0:
            return "short"
        return "long"