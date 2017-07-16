from coinbase.wallet.client import Client


class Coinbase:
    def __init__(self, config):
        api_key = config["coinbase_api"]["key"]
        api_secret = config["coinbase_api"]["secret"]
        self.client = Client(api_key, api_secret)

        self.accumulated_profit_btc = 0
        self.accumulated_profit_eth = 0

    def set_eth_price(self, price):
        self.current_eth_price = price

    def get_exchange_rate(self, coin="BTC", currency="USD"):
        """ Get BTC - USD exchange rate
            Bug for ETH-USD:
            https://community.coinbase.com/t/python-3-5-get-spot-price-for-eth-eur-returns-btc-usd/14273/9
            Modify source library code:
            https://stackoverflow.com/a/23075617/3751589
        """
        param = "{}-{}".format(coin, currency)
        return self.client.get_spot_price(currency_pair=param)

    def calculate_profit_loss(self):
        self.current_btc_price = float(self.get_exchange_rate("BTC", "USD").amount)

        # Get all accounts listing
        accounts = self._get_accounts()
        print("Accounts retrieved: {}\n".format(len(accounts.data)))

        # Read each account
        for account in accounts.data:
            currency = account.balance.currency
            if currency in ("USD", "LTC") or account.name == "My Vault":
                continue

            print("Calculating currency: {}".format(currency))
            print("{}: {} {}".format(account.name, account.balance.amount, currency))

            # Get all transactions
            transactions = account.get_transactions()
            for transaction in transactions.data:
                if transaction.status != "completed":
                        print("Incomplete transaction")
                        continue

                # Calculate for each transaction type
                if transaction.type == "buy":
                    transaction_id = transaction.buy.id
                    transaction_detail = self._get_buy_transaction(account.id,
                                                                   transaction_id)

                    # Calculate price point during purchase
                    amount_paid = float(transaction_detail.subtotal.amount)  # Before fees
                    coins_bought = float(transaction_detail.amount.amount)
                    purchase_price = amount_paid / coins_bought

                    # Calculate profit-loss
                    if currency == "BTC":
                        self.accumulated_profit_btc += (self.current_btc_price - purchase_price) * coins_bought
                        print("\tBuy transaction: {}".format((self.current_btc_price - purchase_price) * coins_bought))
                    elif currency == "ETH":
                        self.accumulated_profit_eth += (self.current_eth_price - purchase_price) * coins_bought
                        print("\tBuy transaction: {}".format((self.current_eth_price - purchase_price) * coins_bought))

                elif transaction.type in ("sell", "send"):
                    # Amount received after fees
                    amount_received = float(transaction.native_amount.amount)

                    # Sell should be positive since it is gain
                    if transaction.type == "sell":
                        amount_received *= -1

                    # Accumulate profit-loss
                    if currency == "BTC":
                        self.accumulated_profit_btc += amount_received
                    elif currency == "ETH":
                        self.accumulated_profit_eth += amount_received

                    print("\t{} transaction: {}".format(transaction.type.title(), amount_received))
                else:
                    print("\tUnknown transaction type: {}".format(transaction.type))
                    print(transaction)
                    continue

            # Print accumulated profit/loss
            if currency == "BTC":
                print("\nProfit/Loss ({}): {}\n".format(currency, self.accumulated_profit_btc))
            elif currency == "ETH":
                print("\nProfit/Loss ({}): {}\n\n".format(currency, self.accumulated_profit_eth))

    def _get_accounts(self):
        return self.client.get_accounts()

    def _get_buy_transaction(self, account_id, transaction_id):
        return self.client.get_buy(account_id,
                                   transaction_id)
