
import telethon
import os

# 需要设置参数, 在Telegram.txt 中设置参数
# Create App in my.telegram.org, you will get api_id and api_hash
api_id = 0
api_hash = '0'
# 通过 my_event_handler1 中接受全部信息，查看log，来找所需要的 group id 和user id
telegram_group_id = 0
telegram_user_id = 0
####################
SCHWAB_USERNAME = ""
SCHWAB_PASSWORD = ""
SCHWAB_TOTP_SECRET = ""
SCHWAB_ACCOUNT = ""
####################
IBKR_account = ""
IBKR_password = ""
IBKR_symbol_id = ""
IBKR_symbol_value_price_ratio = 0
####################
MT5_symbol = ""


cur_dir = os.path.dirname(__file__)

with open(os.path.join(cur_dir, 'Telegram.txt')) as f:
    lines = f.readlines()
    api_id = int(lines[0][lines[0].index('=') + 1:])
    api_hash = lines[1][lines[1].index('=') + 1:].strip()
    telegram_group_id = int(lines[2][lines[2].index('=') + 1:])
    telegram_user_id = int(lines[3][lines[3].index('=') + 1:])
    SCHWAB_USERNAME = lines[4][lines[4].index('=') + 1:].strip()
    SCHWAB_PASSWORD = lines[5][lines[5].index('=') + 1:].strip()
    SCHWAB_TOTP_SECRET = lines[6][lines[6].index(
        '=') + 1:].strip()
    SCHWAB_ACCOUNT = int(lines[7][lines[7].index('=') + 1:])

    IBKR_account = lines[8][lines[8].index('=') + 1:].strip()
    IBKR_username = lines[9][lines[9].index(
        '=') + 1:].strip()
    IBKR_symbol_id = lines[10][lines[10].index('=') + 1:].strip()
    IBKR_symbol_value_price_ratio = int(
        lines[11][lines[11].index('=') + 1:].strip())
    MT5_symbol = lines[12][lines[12].index('=') + 1:].strip()


def get_group_id(peer_id):
    if isinstance(peer_id, telethon.tl.types.PeerChat):
        return peer_id.chat_id
    elif isinstance(peer_id, telethon.tl.types.PeerChannel):
        return peer_id.channel_id
    elif isinstance(peer_id, telethon.tl.types.PeerUser):
        return peer_id.user_id


print("\n**Parameter**\napi_id:{} \napi_hash: {} \ntelegram_group_id: {} \ntelegram_user_id: {} \nSCHWAB_USERNAME: {} \nSCHWAB_PASSWORD: {} \nSCHWAB_TOTP_SECRET: {} \nSCHWAB_ACCOUNT: {} \nIBKR_account: {} \nIBKR_username: {} \nIBKR_symbol_id: {} \nIBKR_symbol_value_price_ratio: {} \nMT5_symbol: {}".format(
    api_id, api_hash, telegram_group_id, telegram_user_id, SCHWAB_USERNAME, SCHWAB_PASSWORD, SCHWAB_TOTP_SECRET, SCHWAB_ACCOUNT, IBKR_account, IBKR_username, IBKR_symbol_id, IBKR_symbol_value_price_ratio,MT5_symbol))
