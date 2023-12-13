import MetaTrader5 as mt5
import time
import pytz
from datetime import datetime
from schwab_api import Schwab
import pprint

SCHWAB_USERNAME=""
SCHWAB_PASSWORD=""
SCHWAB_TOTP_SECRET=""
SCHWAB_ACCOUNT= 0

# the portion of schwab
factor = 0.25

# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()

# Initialize our schwab instance
api = Schwab()

def is_market_opened() -> bool:
    dt = datetime.now(pytz.timezone('US/Eastern'))
    print(dt)
    return 0 <= dt.weekday() <= 4 and 9*60+30 <= dt.hour*60+dt.minute <= 16*60


account_info_dict = mt5.account_info()._asdict()
for prop in account_info_dict:
    print("  {}={}".format(prop, account_info_dict[prop]))

schwab_logged_in = api.login(
    username=SCHWAB_USERNAME,
    password=SCHWAB_PASSWORD,
    totp_secret=SCHWAB_TOTP_SECRET # Get this by generating TOTP at https://itsjafer.com/#/schwab
)

# Get information about all accounts holdings
print("Getting account holdings information")

pprint.pprint(api.get_account_info())

while True:
    if not is_market_opened():
        print('not in market hour, sleep 60s')
        time.sleep(60)
        continue
    
    mt5_positions=mt5.positions_get()
    pprint.pprint(mt5_positions)
    mt5_balance = mt5.account_info().balance
    leverage = 0
    for position in mt5_positions:
        trade_contract_size=mt5.symbol_info(position.symbol).trade_contract_size
        leverage += (position.volume * position.price_open * trade_contract_size)/mt5_balance

    print('MT5 leverage:', leverage)
    account_info = api.get_account_info()[SCHWAB_ACCOUNT]
    available_cash = account_info['available_cash']
    market_value = account_info['market_value']
    account_value = account_info['account_value']
    xxxx_price = 25
    xxxx_qty = 0
    for p in account_info['positions']:
        if p['symbol'] == 'XXXX':
            xxxx_price = p['market_value']
            xxxx_qty += p['quantity']
    diff = leverage * factor * account_value - market_value
    print("Schwab available_cash: {}, market_value: {}, account_value: {}, xxxx_price: {}, xxxx_qty: {}, diff: {}".format(available_cash, market_value,account_value, xxxx_price, xxxx_qty, diff))
    if abs(diff) < 0.01 * account_value:
        time.sleep(10)
        continue
    side = 'Buy' if diff > 0 else 'Sell'

    qty = int(min(abs(diff), available_cash) / xxxx_price) - 1
    if leverage == 0:
        qty = xxxx_qty -1
    print('side:', side, 'qty:', qty)
    messages, success = api.trade(
        ticker="XXXX", 
        side=side, #or Sell
        qty=1, 
        account_id=47198592, # Replace with your account number
        dry_run=False # If dry_run=True, we won't place the order, we'll just verify it.
    )

    print("The order verification was " + "successful" if success else "unsuccessful")
    # print("The order verification produced the following messages: ")
    print(messages)
    time.sleep(10)
    


# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()


