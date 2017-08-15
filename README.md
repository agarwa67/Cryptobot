# Cryptobot
This is an on-going project to create a useful bot for tracking your cryptocurrency portfolio.  

<b>Exchanges supported:</b> Coinbase  
<b>Info needed:</b> API key 

Current features:
- List all transactions by coin
- Calculate profit/loss for each coin (value in USD, % change)
- Calculate profit/loss for entire portfolio
- Supports multiple accounts within Coinbase and allows manual input of external balances

Future features:
- Support other exchanges (Bittrex, Kraken)
- Automate external balance import from other exchanges/Coinigy

Installation steps:
1. sudo apt install python3-pip
2. sudo pip3 install coinbase
3. Log on CoinBase. Navigate to Settings --> API Access --> + New API Key
4. Select the accounts you want to use the bot on and all permissions that end in ":read"
![alt text](https://raw.githubusercontent.com/username/projectname/branch/path/to/img.png)
5. Record your API public and secret key somewhere safe
6. Enter your API keys into config.json
7. python3 main.py to run script

