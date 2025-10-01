from dataclasses import dataclass


@dataclass
class SupportedExchanges:
    spot_exchanges: list[str]
    swap_exchanges: list[str]
    futures_exchanges: list[str]