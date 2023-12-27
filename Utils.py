
import telethon
import os


cur_dir = os.path.dirname(__file__)

with open(os.path.join(cur_dir, 'Telegram.txt')) as f:
    lines = f.readlines()
    api_id = int(lines[0][lines[0].index('=') + 1:])
    api_hash = lines[1][lines[1].index('=') + 1:].strip()
    telegram_group_id = int(lines[2][lines[2].index('=') + 1:])
    telegram_user_id = int(lines[3][lines[3].index('=') + 1:])
    mt5_symbol = lines[4][lines[4].index('=') + 1:].strip()
    mt5_leverage = float(lines[5][lines[5].index('=') + 1:].strip())

    schwab_username = lines[6][lines[6].index('=') + 1:].strip()
    schwab_password = lines[7][lines[7].index('=') + 1:].strip()
    schwab_totp_secret = lines[8][lines[8].index(
        '=') + 1:].strip()
    schwab_account = int(lines[9][lines[9].index('=') + 1:].strip())
    # use 
    schwab_fund_portion_trade = float(lines[10][lines[10].index('=') + 1:].strip())

    ibkr_account = lines[11][lines[11].index('=') + 1:].strip()
    ibkr_symbol = lines[12][lines[12].index('=') + 1:].strip()
    ibkr_leverage = float(lines[13][lines[13].index('=') + 1:].strip())


def get_group_id(peer_id):
    if isinstance(peer_id, telethon.tl.types.PeerChat):
        return peer_id.chat_id
    elif isinstance(peer_id, telethon.tl.types.PeerChannel):
        return peer_id.channel_id
    elif isinstance(peer_id, telethon.tl.types.PeerUser):
        return peer_id.user_id


print("\n**Parameter**\n api_id:{}\n api_hash: {} \n telegram_group_id: {} \n telegram_user_id: {} \n mt5_symbol: {} \n mt5_leverage: {} \n schwab_username: {} \n schwab_password: {} \n schwab_totp_secret: {} \n schwab_account: {} \n schwab_fund_portion_trade: {} \n ibkr_account: {} \n ibkr_symbol: {} \n ibkr_leverage: {}".format(
    api_id, api_hash, telegram_group_id, telegram_user_id, mt5_symbol, mt5_leverage, schwab_username, schwab_password, schwab_totp_secret, schwab_account, schwab_fund_portion_trade, ibkr_account, ibkr_symbol, ibkr_leverage))
