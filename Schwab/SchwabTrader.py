import sys
import os
import MetaTrader5 as mt5
import pytz
import datetime
import telethon

cur_dir = os.path.split(os.path.abspath(__file__))[0]
config_path = os.path.join(cur_dir, '..')
sys.path.append(config_path)
from local_schwab_api import Schwab
from Utils import *

symbol_to_trade = 'XXXX'


class Trader():

    __slots__ = 'api', 'direction_buy', 'direction_sell', 'fund_info', 'log'

    def __init__(self) -> None:
        self.api = Schwab()
        res = self.api.login(
            username=schwab_username,
            password=schwab_password,
            totp_secret=schwab_totp_secret
        )
        self.fund_info = {}
        self.get_fund_info()
        self.direction_buy = 'Buy'
        self.direction_sell = 'Sell'
        print('Schwab login was', "successful" if res else "unsuccessful")

    def get_fund_info(self):
        all_acount_info = self.api.get_account_info_v2()
        print('all_acount_info', all_acount_info)
        for key in all_acount_info:
            self.fund_info[key] = self.get_account_info(
                all_acount_info[key], symbol_to_trade)

    def get_account_info(self, account_info, symbol):
        account_value, settled_fund, symbol_price, symbol_position_volume = 0, 0, 30, 0
        account_value = account_info['account_value']
        settled_fund = account_info['settled_fund']
        for p in account_info['positions']:
            if p['symbol'] == symbol:
                symbol_price = p['market_value'] / p['quantity']
                symbol_position_volume += p['quantity']
        return account_value, settled_fund, symbol_price, symbol_position_volume

    def trade_all_accounts(self, symbol, portion, direction='Buy', for_testing=False):
        self.log = ''
        for account in schwab_account:
            self.trade(account, symbol, portion, direction, for_testing)
            

    def trade(self, account, symbol, portion, direction='Buy', for_testing=False):
        self.append_log('{} Going to {} {} with portion {} on account {} '.format(('TESTING' if for_testing else ''), direction, symbol, portion, account))
        print(self.fund_info[account])
        all_acount_info = self.api.get_account_info()
        account_value, settled_fund, symbol_price, symbol_position_volume = 0, 0, 30, 0
        for key in all_acount_info:
            symbol_price1 = self.get_account_info(
                all_acount_info[key], symbol)[2]
            if key == account:
                account_value, settled_fund, symbol_price, symbol_position_volume = self.get_account_info(
                    all_acount_info[key], symbol)
        symbol_price = symbol_price1

        if account_value == 0:
            account_value, settled_fund, symbol_price, symbol_position_volume = self.fund_info[account]
        fund_to_use = min(portion * account_value, settled_fund)
        volume = int(min(fund_to_use * 0.99, fund_to_use - symbol_price * 2) /
                     symbol_price) if direction == self.direction_buy else symbol_position_volume - 1
        if direction == self.direction_buy:
            volume -= symbol_position_volume

        if volume < 1:
            s = 'Did not place order on schwab, volume is too small, volume: {}'.format(volume)
            self.append_log(s)
            print(s)
            return
        s = "Going to {} {} {} for account {} ,settled_fund: {}, account_value: {}, symbol_price: {}, ".format(
            direction, volume, symbol, account, settled_fund, account_value, symbol_price)
        print(s)
        self.append_log(s)

        messages, success = self.api.trade(
            ticker=symbol,
            side=direction,  # 'Buy' or 'Sell'
            qty=volume,
            account_id=account,  # Replace with your account number
            # If dry_run=True, we won't place the order, we'll just verify it.
            dry_run=for_testing
        )
        if success and not for_testing:
            self.fund_info[account] = account_value, settled_fund - (
                symbol_price * volume if direction == 'Buy' else 0), symbol_price, symbol_position_volume + (volume if direction == 'Buy' else -volume)
        s = "The schwab order verification was " + "successful" if success else "unsuccessful"
        print(s)
        self.append_log(s+'\n')
        # print(messages)
    def append_log(self, s):
        self.log += (s + '\n')


client = telethon.TelegramClient('anon', api_id, api_hash)
trader = Trader()

async def check_channel():
    chat_ids = {}
    async for dialog in client.iter_dialogs():
        chat_ids[str(dialog.id)] = dialog.name
    print(chat_ids)
    for k,v in chat_ids.items():
            pass

with client:
    client.loop.run_until_complete(check_channel())

async def send_message(msg):
    await client.send_message(telegram_log_group_id, msg)

with client:
    client.loop.run_until_complete(send_message('schwab trader started\n' + str(trader.fund_info)))

print('\n*** Preview of placing order, for testing, not real trade ***\n')
trader.trade_all_accounts(symbol=symbol_to_trade,
                          portion=schwab_fund_portion_trade, for_testing=True)
print()


@client.on(telethon.events.NewMessage())
async def my_event_handler1(event):
    now = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    group_id = event.message.peer_id
    peer_id = event.message.peer_id
    group_id = get_group_id(peer_id)
    user_id = event.message.from_id.user_id if event.message.from_id else -1
    sms = event.raw_text.lower()
    # 第一次运行时，通过log 获得group id 和user id， 填到Telegram.txt 中

    if now.hour >=17 or now.hour < 9 or now.weekday >=5:
        await client.send_message(telegram_log_group_id, 'schwab trader exit')
        exit()
    print('message:', sms, ', group id:', group_id,
          ', user id:', user_id, ' , time:', now.strftime('%Y-%m-%d %H:%M:%S'))

    if group_id == telegram_group_id and user_id == telegram_user_id:
        if 'buy spx' in sms:
            print('Going to buy on schwab')
            trader.trade_all_accounts(symbol_to_trade,
                                      schwab_fund_portion_trade)
            await client.send_message(telegram_log_group_id, trader.log)
        if 'sell spx' in sms:
            print('Going to sell all {} position on schwab'.format(symbol_to_trade))
            trader.trade_all_accounts(symbol_to_trade,
                                      schwab_fund_portion_trade, direction='Sell')
            await client.send_message(telegram_log_group_id, trader.log)
    print()





client.start()
client.run_until_disconnected()
