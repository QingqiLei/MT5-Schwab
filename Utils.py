
import telethon
import os


cur_dir = os.path.dirname(__file__)


with open(os.path.join(cur_dir, 'Telegram.txt'), 'r', encoding='UTF-8') as f:
    lines = f.readlines()
    index = 0

    def parse_string():
        global index
        res = lines[index][lines[index].index('=') + 1:].strip()
        index +=1
        return res


    api_id = int(parse_string())
    api_hash = parse_string()
    telegram_group_id = int(parse_string())
    telegram_user_id = int(parse_string())

    telegram_log_group_id = int(parse_string())

    mt5_symbol = parse_string()
    mt5_leverage = float(parse_string())
    

    schwab_username = parse_string()
    schwab_password = parse_string()
    schwab_totp_secret = parse_string()
    schwab_account = [int(a) for a in parse_string().split(',')]

    # use
    schwab_fund_portion_trade = float(parse_string())

    ibkr_account = parse_string()
    ibkr_symbol = parse_string()
    ibkr_leverage = float(parse_string())


def get_group_id(peer_id):
    if isinstance(peer_id, telethon.tl.types.PeerChat):
        return peer_id.chat_id
    elif isinstance(peer_id, telethon.tl.types.PeerChannel):
        return peer_id.channel_id
    elif isinstance(peer_id, telethon.tl.types.PeerUser):
        return peer_id.user_id


print("\n**Parameter**\n api_id:{}\n api_hash: {} \n telegram_group_id: {} \n telegram_user_id: {} \n telegram_log_group_id: {} \n mt5_symbol: {} \n mt5_leverage: {} \n schwab_username: {} \n schwab_password: {} \n schwab_totp_secret: {} \n schwab_account: {} \n schwab_fund_portion_trade: {} \n ibkr_account: {} \n ibkr_symbol: {} \n ibkr_leverage: {}".format(
    api_id, api_hash, telegram_group_id, telegram_user_id, telegram_log_group_id, mt5_symbol, mt5_leverage, schwab_username, schwab_password, schwab_totp_secret, schwab_account, schwab_fund_portion_trade, ibkr_account, ibkr_symbol, ibkr_leverage))
