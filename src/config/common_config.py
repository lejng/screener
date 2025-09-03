from pathlib import Path

import yaml


class CommonConfig:

    def __init__(self, config_file_name: str):
        self.config_file_name: str = config_file_name
        self.config = self.read_config()
        self.default_min_spread: str = "1"
        self.default_amount_in_quote = "100"

    def reload_config(self):
        self.config = self.read_config()

    def read_config(self):
        base_dir = Path(__file__).resolve().parents[2]
        path_to_file = base_dir / "resources" / self.config_file_name
        with open(path_to_file, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def get_spot_exchanges(self) -> list[str]:
        names :list[str] = self.config["exchanges"]["spot"].split(",")
        return names

    def get_swap_exchanges(self) -> list[str]:
        names :list[str] = self.config["exchanges"]["swap"].split(",")
        return names

    def get_futures_exchanges(self) -> list[str]:
        names :list[str] = self.config["exchanges"]["futures"].split(",")
        return names

    def get_exchanges_for_fetch_top_fundings(self) -> list[str]:
        names :list[str] = self.config["exchanges"]["fundings"].split(",")
        return names

    def get_min_spread(self) -> float:
        try:
            return float(self.config["min_spread"] or self.default_min_spread)
        except ValueError:
            return 1

    def get_amount_in_quote(self) -> float:
        try:
            return float(self.config["amount_in_quote"] or self.default_amount_in_quote)
        except ValueError:
            return 100