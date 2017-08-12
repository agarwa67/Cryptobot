from coinbase.wallet.client import Client
from pprint import pprint

class Coinbase:
    def __init__(self, config):
        account = input("Account: ")
        if account == "Kevin":
            api_key = config["coinbase_api_kevin"]["key"]
            api_secret = config["coinbase_api_kevin"]["secret"]
        elif account == "Liang":
            api_key = config["coinbase_api_liang"]["key"]
            api_secret = config["coinbase_api_liang"]["secret"]
        else:
            print("Account not found. Please add API keys to config.json")
        self.client = Client(api_key, api_secret)

        self.accumulated_profit_btc = 0
        self.accumulated_profit_eth = 0

    def set_eth_price(self, price):
        self.current_eth_price = price
        # TODO automatically update ETH price

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
        # self.current_eth_price = float(self.get_exchange_rate("ETH", "USD").amount)

        # Ask for balance outside of Coinbase
        BTC_external_balance = float(input('BTC external balance: '))
        ETH_external_balance = float(input('ETH external balance: '))

        # Get all accounts listing
        accounts = self._get_accounts()
        print("Accounts retrieved: {}\n".format(len(accounts.data)))

        # Read each account
        for account in accounts.data:
            currency = account.balance.currency
            if currency in ("USD", "LTC") or account.name == "My Vault": # Ignore these accounts
                continue
            print(currency)

            print("Calculating currency: {}".format(currency))
            print("{}: {} {}".format(account.name, account.balance.amount, currency))

            # Get all transactions
            transactions = account.get_transactions(start_after="1805ae5b-f65b-5825-b780-9c6cecdec1cf", limit=100)
            """ Documentation for argument syntax in get_transactions
                https://github.com/coinbase/coinbase-python/blob/f9ed2249865c2012e3b86106dad5f8c6068366ed/coinbase/wallet/model.py#L168
            """
            # TODO regex or some way to find everyones start_after
            for transaction in transactions.data:
                if transaction.status != "completed":
                        print("Incomplete transaction")
                        continue

            # Calculate for each transaction type
                # Calculate all BUYS
                if transaction.type == "buy":
                    transaction_id = transaction.buy.id
                    transaction_detail = self._get_buy_transaction(account.id,
                                                                   transaction_id)

                    # Calculate price point during purchase
                    amount_paid = float(transaction_detail.subtotal.amount)  # Before fees
                    coins_bought = float(transaction_detail.amount.amount)
                    purchase_price = amount_paid / coins_bought # Price of BTC/ETH at time of buying
                    amount_paid_fees = float(transaction.native_amount.amount) # After fees

                    # Calculate profit-loss
                    if currency == "BTC":
                        self.accumulated_profit_btc -= amount_paid_fees
                        #TODO prompt user if they want to print all transactions
                        print("\tBuy transaction: -{}".format(amount_paid_fees))
                    elif currency == "ETH":
                        self.accumulated_profit_eth -= amount_paid_fees
                        print("\tBuy transaction: -{}".format(amount_paid_fees))
                        #TODO prompt user if they want to print all transactions

                # Calculate all SELLS
                elif transaction.type in ("sell"):
                    # Amount received after fees
                    amount_received = float(transaction.native_amount.amount)
                    amount_received = amount_received * -1

                    # Accumulate profit-loss
                    if currency == "BTC":
                        self.accumulated_profit_btc += amount_received
                    elif currency == "ETH":
                        self.accumulated_profit_eth += amount_received

                    #TODO prompt user if they want to print all transactions
                    print("\t{} transaction: {}".format(transaction.type.title(), amount_received))

            # Add current balance in account + current external balance to profit/Loss
            if currency == "BTC":
                # BTC_external_value = BTC_external_balance * self.btc_current_price
                account.balance.amount = float(account.balance.amount)
                self.accumulated_profit_btc += (BTC_external_balance + account.balance.amount) * self.current_btc_price
            elif currency == "ETH":
                # ETH_external_value = ETH_external_balance * self.eth_current_price
                account.balance.amount = float(account.balance.amount)
                self.accumulated_profit_eth += (ETH_external_balance + account.balance.amount) * self.current_eth_price

            # Print accumulated profit/loss
            if currency == "BTC":
                print("\nProfit/Loss ({}): ${}".format(currency, self.accumulated_profit_btc))
            elif currency == "ETH":
                print("\nProfit/Loss ({}): ${}\n".format(currency, self.accumulated_profit_eth))

        # Print total account (BTC + ETH) profit/loss
        print("Profit/Loss (ALL): ${}\n".format(self.accumulated_profit_btc + self.accumulated_profit_eth))
        # TODO limit decimal points after float


    def _get_accounts(self):
        return self.client.get_accounts()

    def _get_buy_transaction(self, account_id, transaction_id):
        return self.client.get_buy(account_id,
                                   transaction_id)
