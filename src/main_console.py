from src.arbitrage.arbitrage_facade import ArbitrageFacade
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
from src.console.console_facade import ConsoleFacade

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

arbitrage_facade = ArbitrageFacade(all_spot_connectors, all_swap_connectors, all_futures_connectors)
console_facade = ConsoleFacade(arbitrage_facade)
while True:
    print("1 - Exit")
    print("2 - Show all types of spreads (spot-spot, spot-swap, spot-futures, swap-swap, all combinations swap and futures)")
    print("3 - Show spreads without transferring (spot-swap, spot-futures, swap-swap, all combinations swap and futures)")
    print("4 - Show spread for coin")
    print("5 - Show top fundings")
    print("6 - Show funding by selected coin")

    command = input("Enter command: ")
    try:
        if command == '1':
            break
        if command == '2':
            console_facade.print_all_spreads()
        if command == '3':
            console_facade.print_spreads_without_transfer()
        if command == '4':
            console_facade.print_spread_for_entered_coin()
        if command == '5':
            console_facade.print_top_funding_rates()
        if command == '6':
            console_facade.print_funding_rate_for_coin()
    except Exception as e:
        print(f"Unexpected error: {e}")