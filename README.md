"# MT5-Schwab" 

## 使用说明

1. TelegramToMT5.py 可以接收特定 Telegram group， user的消息，作为信号来交易标普 SPXm。
2. 包含 "buy spx"的消息是买入信号。包含 "sell spx"的消息是买入信号。大小写都可以
3. 运行程序后，查看log中MT5账号是否是想要交易的账号。 如果电脑上有多个MT5终端，那么会随机选择一个MT5进行交易。所以运行程序后要确认！

## 步骤

### 安装Python
1. 下载https://www.python.org/downloads/release/python-3910/

![Drag Racing](images/pythonDownload.png)

2. 在安装的第一步选择 "Add Python3.9 to PATH"
![Drag Racing](images/pythonInstall1.png)

3. 在Command Prompt 中运行命令来安装所需要的包

`pip install telethon && pip install MetaTrader5`


### 获取 Telegram API 密钥
1. 在 https://my.telegram.org/ 中的 API development tools 创建一个APP，然后就有api_id, api_hash。 填入程序代码中




### 运行程序


1. 第一次运行会需要在log里填写手机号， 会发送验证码到APP里，填写验证码即可。

2. 确定group id， user id。 确保 my_event_handler1 上面使用`@client.on(events.NewMessage())`, 来接受所有消息。 发送一条消息，然后在log 中查看
Telegram log 示例。 channel_id 是 1992922380， user_id 是 5138637335。 将channel_id 和user_id 填入程序中
`NewMessage.Event(original_update=UpdateNewChannelMessage(message=Message(id=79, peer_id=PeerChannel(channel_id=1992922380), ...... from_id=PeerUser(user_id=5138637335),  ......`

3. 正式运行程序， 注意查看输出确定MT5信息是否正确。注意电脑不要休眠、关机。