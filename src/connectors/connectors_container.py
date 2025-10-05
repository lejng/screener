from src.connectors.future.bybit_future_connector import BybitFutureConnector
from src.connectors.future.future_common_connector import FutureCommonConnector
from src.connectors.future.gate_future_connector import GateFutureConnector
from src.connectors.spot.binance_spot_connector import BinanceSpotConnector
from src.connectors.spot.bitget_spot_connector import BitgetSpotConnector
from src.connectors.spot.bybit_spot_connector import BybitSpotConnector
from src.connectors.spot.gate_spot_connector import GateSpotConnector
from src.connectors.spot.kucoin_spot_connector import KucoinSpotConnector
from src.connectors.spot.mexc_spot_connector import MexcSpotConnector
from src.connectors.spot.okx_spot_connector import OkxSpotConnector
from src.connectors.spot.spot_common_connector import SpotCommonConnector
from src.connectors.swap.binance_swap_connector import BinanceSwapConnector
from src.connectors.swap.bitget_swap_connector import BitgetSwapConnector
from src.connectors.swap.bybit_swap_connector import BybitSwapConnector
from src.connectors.swap.gate_swap_connector import GateSwapConnector
from src.connectors.swap.hyperliquid_swap_connector import HyperliquidSwapConnector
from src.connectors.swap.kucoin_swap_connector import KucoinSwapConnector
from src.connectors.swap.mexc_swap_connector import MexcSwapConnector
from src.connectors.swap.okx_swap_connector import OkxSwapConnector
from src.connectors.swap.paradex_swap_connector import ParadexSwapConnector
from src.connectors.swap.swap_common_connector import SwapCommonConnector

all_spot_connectors: list[SpotCommonConnector] = [
        BybitSpotConnector(),
        GateSpotConnector(),
        KucoinSpotConnector(),
        BinanceSpotConnector(),
        MexcSpotConnector(),
        BitgetSpotConnector(),
        OkxSpotConnector()
    ]

all_swap_connectors: list[SwapCommonConnector] = [
        BybitSwapConnector(),
        GateSwapConnector(),
        KucoinSwapConnector(),
        HyperliquidSwapConnector(),
        ParadexSwapConnector(),
        BinanceSwapConnector(),
        MexcSwapConnector(),
        BitgetSwapConnector(),
        OkxSwapConnector()
    ]

all_futures_connectors: list[FutureCommonConnector] = [
        BybitFutureConnector(),
        GateFutureConnector()
    ]