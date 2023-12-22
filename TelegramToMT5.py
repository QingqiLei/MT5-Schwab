import MetaTrader5 as mt5
import telethon
import datetime
import pytz

# 使用 comment 来区分仓位， 固定 交易品种 杠杆 stop loss
intraday_comment = 'intraday'
symbol = 'SPXm'
leverage = 0.5
stop_loss = 15

# 需要设置参数, 在Telegram.txt 中设置参数
# Create App in my.telegram.org, you will get api_id and api_hash
api_id = 0
api_hash = '0'
# 通过 my_event_handler1 中接受全部信息，查看log，来找所需要的 group id 和user id
telegram_group_id = 0
telegram_user_id = 0
####################

with open('Telegram.txt') as f:
    lines = f.readlines()
    api_id = int(lines[0][lines[0].index('=') + 1:])
    api_hash = lines[1][lines[1].index('=') + 1:]
    telegram_group_id = int(lines[2][lines[2].index('=') + 1:])
    telegram_user_id = int(lines[3][lines[3].index('=') + 1:])

print('api_id=', api_id, ' ,api_hash=', api_hash, ' ,telegram_group_id=',
      telegram_group_id, ' ,telegram_user_id=', telegram_user_id, '\n')

mt5.initialize()
client = telethon.TelegramClient('anon', api_id, api_hash)

def trade_long(comment, leverage, allow_more=False):
    '''
    Buy
    comment: Add a comment to the position to classify them
    leverage: the leverage
    '''
    positions = mt5.positions_get()
    already_bought = False
    # if already bought and don't allow to buy more than one, stop buying.
    if (positions and len(positions) > 0):
        for position in positions:
            already_bought |= position.comment == comment
    if already_bought and not allow_more:
        print('Already bought, can not buy more')
        return

    balance = mt5.account_info().balance
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, 'is not found in MT5')
        return

    # if the symbol is unavailable in MarketWatch, add it
    if not symbol_info.visible:
        if not mt5.symbol_select(symbol, True):
            print("symbol_select({}}) failed, exit", symbol)
            return

    # Calculate volume and buy at market price
    price = mt5.symbol_info_tick(symbol).bid
    trade_contract_size = symbol_info.trade_contract_size
    volume_step = symbol_info.volume_step
    volume_format = ("{:."+str(len(str(volume_step))-2)+"f}")
    volume = float(volume_format.format(
        (balance * leverage/(price * trade_contract_size))))
    print('price=', price, ', trade_contract_size=', trade_contract_size,
          ', volume_step=', volume_step, ', volume=', volume)
    sl = price - stop_loss

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "sl": sl,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
    }

    # Send market order
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print('Failed to buy ' + symbol +
              ', cause=' + result._asdict()['comment'])
    else:
        print('Success to buy ' +
              str(float("{:.2f}".format(volume))) + ' '+symbol)


def trade_close(comment, close_all=True):
    '''
    Close all positions that has this comment
    '''
    positions = mt5.positions_get()
    if not (positions and len(positions) > 0):
        print('No position to sell in MT5')
        return

    found = False
    for position in positions:
        if position.comment == comment:
            found = True
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": 1 - position.type,
                "position": position.identifier,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
            }

            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print('Failed to close, cause= ' + result._asdict()['comment'])
            else:
                print('Closed ' + str(position.volume) + ' '+position.symbol +
                      (' with profit ' if position.profit > 0 else ' with loss ') + str(position.profit))
            if not close_all:
                break
    if not found:
        print('no position with comment', comment)


def get_group_id(peer_id):
    if isinstance(peer_id, telethon.tl.types.PeerChat):
        return peer_id.chat_id
    elif isinstance(peer_id, telethon.tl.types.PeerChannel):
        return peer_id.channel_id
    elif isinstance(peer_id, telethon.tl.types.PeerUser):
        return peer_id.user_id


print(' ##### Listening message, please keep MT5 open ##### \n')
MT5_account_info = mt5.account_info()
print('MT5 account:', MT5_account_info.login, ", equity:",
      MT5_account_info.equity, ", server:", MT5_account_info.server, '\n')


fmt = '%Y-%m-%d %H:%M:%S'


@client.on(telethon.events.NewMessage(chats=[telegram_group_id]))
# @client.on(telethon.events.NewMessage())   # 使用上面一行，来只接收特定的group.
async def my_event_handler1(event):
    now = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    group_id = event.message.peer_id
    peer_id = event.message.peer_id
    group_id = get_group_id(peer_id)
    user_id = event.message.from_id.user_id if event.message.from_id else -1
    sms = event.raw_text.lower()

    # 第一次运行时，通过log 获得group id 和user id， 填到Telegram.txt 中
    print('message:', sms, ',group id:', group_id,
          ',user id:', user_id, ' ,time:', now.strftime(fmt))
    MT5_account_info = mt5.account_info()
    print('MT5 account:', MT5_account_info.login, ",equity:",
          MT5_account_info.equity, ",server:", MT5_account_info.server)

    if group_id == telegram_group_id and user_id == telegram_user_id:
        if 'buy spx' in sms:
            print('Going to buy, leverage:', leverage)
            trade_long(intraday_comment, leverage)
        if 'sell spx' in sms:
            print('Going to sell all position')
            trade_close(intraday_comment)
    print()

client.start()
client.run_until_disconnected()
