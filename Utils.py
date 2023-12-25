
import telethon

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


with open('Telegram.txt') as f:
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


def get_group_id(peer_id):
    if isinstance(peer_id, telethon.tl.types.PeerChat):
        return peer_id.chat_id
    elif isinstance(peer_id, telethon.tl.types.PeerChannel):
        return peer_id.channel_id
    elif isinstance(peer_id, telethon.tl.types.PeerUser):
        return peer_id.user_id

print("\n**Parameter**\napi_id:{} \napi_hash: {} \ntelegram_group_id: {} \ntelegram_user_id: {} \nSCHWAB_USERNAME: {} \nSCHWAB_PASSWORD: {} \nSCHWAB_TOTP_SECRET: {} \nSCHWAB_ACCOUNT: {}".format(
    api_id, api_hash, telegram_group_id, telegram_user_id, SCHWAB_USERNAME, SCHWAB_PASSWORD, SCHWAB_TOTP_SECRET, SCHWAB_ACCOUNT))
