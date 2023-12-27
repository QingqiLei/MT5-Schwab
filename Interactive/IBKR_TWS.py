import nest_asyncio
from dateutil.parser import parse
import sys
sys.path.append("..")
from Utils import *
from ib_insync import *
import datetime
import pytz

nest_asyncio.apply()

class Trader:
    def __init__(self, account) -> None:
        self.ib = IB()
        self.ib.connect('127.0.0.1', 7497, clientId=1)
        self.account = account
        fund_info = self.get_fund_info()
        print('\n Account: {} \n NetLiquidation: {} \n AvailableFunds: {}'.format(
            self.account, fund_info[0], fund_info[1]))
        print()

        self.get_positions()

    def get_fund_info(self):
        '''
        return [NetLiquidation, AvailableFunds]
        '''
        res = [-1, -1]
        for t in self.ib.accountSummary():
            if t.account == self.account and t.tag == 'NetLiquidation':
                res[0] = float(t.value)

            if t.account == self.account and t.tag == 'AvailableFunds':
                res[1] = float(t.value)
        return res

    def get_positions(self):
        '''
        return {symbol: [[volume, average cost, conId]]}
        '''
        res = {}
        for p in self.ib.reqPositions():
            if p.account == self.account:
                if p.contract.symbol not in res:
                    res[p.contract.symbol] = []
                res[p.contract.symbol].append(
                    [p.position, p.avgCost, p.contract.conId])
        print(
            'Current positions (format {symbol: [[volume, average cost, conId]]}): ', res)

        return res

    def get_near_future_contract(self, symbol):
        '''
        return a conId, its future is 30 days easier than last trade date
        '''
        mes = Future(symbol)
        self.ib.sleep(2)

        contract_details = self.ib.reqContractDetails(mes)

        contract_details = sorted(
            contract_details, key=lambda a: a.contract.lastTradeDateOrContractMonth)
        today = datetime.datetime.today()

        for contract_detail in contract_details:
            diff = parse(
                contract_detail.contract.lastTradeDateOrContractMonth) - today
            if diff.days > 30:
                return self.ib.qualifyContracts(contract_detail.contract)[0]

    def get_contract_from_conId(self, conId):
        return self.ib.qualifyContracts(Future(conId=conId))[0]

    def get_current_price(self, contract):
        return float(util.df(self.ib.reqHistoricalData(contract=contract, endDateTime='', durationStr='1 D',  barSizeSetting='1 Hour', whatToShow='ASK', useRTH=True)).iloc[-1]['close'])

    def trade_future(self, symbol, leverage, for_testing=False):
        contract = self.get_near_future_contract(symbol)
        current_price = self.get_current_price(contract)
        net_liquidation, available_fund = self.get_fund_info()
        print('Symbol: {}, current_price: {}, net_liquidation: {}, available_fund: {}'.format(
            symbol, current_price, net_liquidation, available_fund))

        volume = round((leverage * net_liquidation) /
                       (current_price * float(contract.multiplier)))
        t= volume
        positions = self.get_positions()
        if symbol in positions:
            current_volume = sum(p[0] for p in positions[symbol])
            if current_volume > 0:
                volume -= current_volume
        
        if volume <= 0:
            if t > 0:
                print('Did not place order on IBKR, already bought enough')
            else:
                print('Did not place order on IBKR, volume is too small, volume:', volume)
            return
        market_order = MarketOrder('BUY', volume)
        self.place_order(contract, market_order, for_testing=for_testing)

    def close(self, symbol, for_testing=False):
        positions = self.get_positions()
        if symbol in positions:
            for volume, average_cost, conId in positions[symbol]:
                if volume == 0:
                    continue

                market_order = MarketOrder(
                    'BUY' if volume < 0 else 'SELL', volume)
                contract = self.get_contract_from_conId(conId)
                self.place_order(contract, market_order,
                                 for_testing=for_testing)

    def place_order(self, contract, order1, for_testing=False):
        if for_testing:
            res = self.ib.whatIfOrder(contract, order1)
            if not res:
                print('Failed to test placing order')
            else:
                print('Success to test placing order')
            return

        order_res = self.ib.placeOrder(contract, order1)  # async

        def orderFilled(trade):
            print('Result of order: \n Symbol: {} \n Last trade date: {} \n Direction: {} \n Status: {} \n Volume filled: {} \n Average price: {} \n message: {}'.format(trade.contract.symbol,
                  trade.contract.lastTradeDateOrContractMonth, trade.order.action, trade.orderStatus.status, trade.orderStatus.filled, trade.orderStatus.avgFillPrice, trade.log[-1].message))
            print()
        order_res.filledEvent += orderFilled
        order_res.cancelledEvent += orderFilled


client = telethon.TelegramClient('anon', api_id, api_hash)
trader = Trader(ibkr_account)

print('\n*** Preview of placing order, for testing, not real trade ***\n')
trader.trade_future(ibkr_symbol, ibkr_leverage, for_testing=True)
print()


@client.on(telethon.events.NewMessage(chats=[telegram_group_id]))
async def my_event_handler1(event):
    now = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    group_id = event.message.peer_id
    peer_id = event.message.peer_id
    group_id = get_group_id(peer_id)
    user_id = event.message.from_id.user_id if event.message.from_id else -1
    sms = event.raw_text.lower()
    # 第一次运行时，通过log 获得group id 和user id， 填到Telegram.txt 中
    print('message:', sms, ', group id:', group_id,
          ', user id:', user_id, ' , time:', now.strftime('%Y-%m-%d %H:%M:%S'))

    if group_id == telegram_group_id and user_id == telegram_user_id:
        if 'buy spx' in sms:
            print('Going to buy on Interactive')
            trader.trade_future(ibkr_symbol, ibkr_leverage)
        if 'sell spx' in sms:
            print('Going to sell all {} position on Interactive'.format(ibkr_symbol))
            trader.close(ibkr_symbol)
    print()

client.start()
client.run_until_disconnected()
