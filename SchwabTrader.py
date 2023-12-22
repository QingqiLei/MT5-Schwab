import MetaTrader5 as mt5
import time
import pytz
from datetime import datetime
from schwab_api import Schwab
import pprint

class Trader():

    __slots__ = "SCHWAB_USERNAME", "SCHWAB_PASSWORD", "SCHWAB_TOTP_SECRET", "SCHWAB_ACCOUNT", "api"


    def __init__(self) -> None:
        self.api = None
        self.SCHWAB_USERNAME = ""
        self.SCHWAB_PASSWORD = ""
        self.SCHWAB_TOTP_SECRET = ""
        self.SCHWAB_ACCOUNT = ""

    def load(self):
        self.load_parameter()
        self.api = Schwab()

        res = self.api.login(
            username=self.SCHWAB_USERNAME,
            password=self.SCHWAB_PASSWORD,
            totp_secret=self.SCHWAB_TOTP_SECRET # Get this by generating TOTP at https://itsjafer.com/#/schwab
        )
        print('Schwab login was', "successful" if res else "unsuccessful")


    def load_parameter(self):
        with open('Telegram.txt') as f:
            lines = f.readlines()
            self.SCHWAB_USERNAME = lines[4][lines[4].index('=') + 1:].strip()
            self.SCHWAB_PASSWORD = lines[5][lines[5].index('=') + 1:].strip()
            self.SCHWAB_TOTP_SECRET = lines[6][lines[6].index('=') + 1:].strip()
            self.SCHWAB_ACCOUNT = int(lines[7][lines[7].index('=') + 1:])
        print('SCHWAB_USERNAME=', self.SCHWAB_USERNAME, '\nSCHWAB_PASSWORD=', self.SCHWAB_PASSWORD, '\nSCHWAB_TOTP_SECRET=', self.SCHWAB_TOTP_SECRET, '\nSCHWAB_USERNAME=', self.SCHWAB_ACCOUNT, '\n')

    def trade(self, symbol, portion, direction = 'Buy', for_testing = False):
        account_info = self.api.get_account_info()[self.SCHWAB_ACCOUNT]
        print('Schwab account info:', account_info)
        
        account_value = account_info['account_value']
        settled_fund = account_info['settled_fund']
        quotes = self.api.quote_v2(["PFE", "AAPL"])
        symbol_price = 30
        symbol_position_volume = 0

        for p in account_info['positions']:
            if p['symbol'] == symbol:
                symbol_price = p['market_value'] / p['quantity']
                symbol_position_volume += p['quantity']

        volume = int(min(portion * account_value, settled_fund) / symbol_price) - 1  if direction == 'Buy' else symbol_position_volume - 1

        if volume < 1:
            print('Did not place order on schwab, volume is too small, volume:', volume)
            return
        print("Going to {} {} {} ,settled_fund: {}, account_value: {}, symbol_price: {}".format(direction, volume, symbol, settled_fund,account_value, symbol_price))
        
        messages, success = self.api.trade(
            ticker=symbol, 
            side=direction, # 'Buy' or 'Sell'
            qty=volume, 
            account_id=self.SCHWAB_ACCOUNT, # Replace with your account number
            dry_run=for_testing # If dry_run=True, we won't place the order, we'll just verify it.
        )
        print("The schwab order verification was " + "successful" if success else "unsuccessful")
        # print(messages)


