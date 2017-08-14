import json
from pprint import pprint
from exchanges.coinbase_pkg import Coinbase


def get_config():
    with open("config.json") as f:
        return json.load(f)


def main():
    config = get_config()

    # Coinbase
    coinbase = Coinbase(config)
    coinbase.set_eth_price(297.00)
    coinbase.calculate_profit_loss()


if __name__ == "__main__":
    main()
