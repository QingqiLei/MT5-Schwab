import MetaTrader5 as mt5
import pytz
import datetime
from schwab_api import Schwab
import telethon
from Utils import *

portion = 0.33
symbol = 'XXXX'


class Trader():

    __slots__ = "api"

    def __init__(self) -> None:
        self.api = Schwab()
        res = self.api.login(
            username=SCHWAB_USERNAME,
            password=SCHWAB_PASSWORD,
            totp_secret=SCHWAB_TOTP_SECRET
        )
        print('Schwab login was', "successful" if res else "unsuccessful")

    def trade(self, symbol, portion, direction='Buy', for_testing=False):
        account_info = self.api.get_account_info()[SCHWAB_ACCOUNT]
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

        volume = int(min(portion * account_value, settled_fund) / symbol_price) - \
            1 if direction == 'Buy' else symbol_position_volume - 1

        if volume < 1:
            print('Did not place order on schwab, volume is too small, volume:', volume)
            return
        print("Going to {} {} {} ,settled_fund: {}, account_value: {}, symbol_price: {}".format(
            direction, volume, symbol, settled_fund, account_value, symbol_price))

        messages, success = self.api.trade(
            ticker=symbol,
            side=direction,  # 'Buy' or 'Sell'
            qty=volume,
            account_id=SCHWAB_ACCOUNT,  # Replace with your account number
            # If dry_run=True, we won't place the order, we'll just verify it.
            dry_run=for_testing
        )
        print("The schwab order verification was " +
              "successful" if success else "unsuccessful")
        # print(messages)


client = telethon.TelegramClient('anon', api_id, api_hash)
trader = Trader()


@client.on(telethon.events.NewMessage(chats=[telegram_group_id]))
async def my_event_handler1(event):
    now = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    group_id = event.message.peer_id
    peer_id = event.message.peer_id
    group_id = get_group_id(peer_id)
    user_id = event.message.from_id.user_id if event.message.from_id else -1
    sms = event.raw_text.lower()

    if group_id == telegram_group_id and user_id == telegram_user_id:
        if 'buy spx' in sms:
            print('Going to buy on schwab')
            trader.trade(symbol, portion)
        if 'sell spx' in sms:
            print('Going to sell all position on schwab')
            trader.trade(symbol, portion, direction='Sell')
    print()

client.start()
client.run_until_disconnected()
