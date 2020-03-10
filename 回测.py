import tushare as ts
import pandas as pd
import numpy as np
import time

class Huice:
    fund = 0; # 初始资金
    remaining = 0; # 寸头
    open_tax = 0; # 开仓印花税
    open_commission = 0; # 开仓佣金
    close_tax = 0; # 平仓印花税
    close_commission = 0; # 平仓佣金
    min_commission = 0; # 最低佣金
    hold_stocks = {}; # 持仓股票
    raw_transaction_list = []; # 原交易队列
    df = pd.DataFrame(columns=['stock_code', 'stock_number', 'date', 'price', 'buy'])

    def __init__(self, fund):# 初始化资金，也是持仓资金
        self.fund = fund
        self.remaining = fund
    def set_order_cost(self, open_tax, open_commission, close_tax, close_commission, min_commission): # 设置交易费用
        self.open_tax = open_tax
        self.open_commission = open_commission
        self.close_tax = close_tax
        self.close_commission = close_commission
        self.min_commission = min_commission
    def getRawData(self, list): # 传递原交易队列
        for item in list:
            self.raw_transaction_list.append(item)
        self.makeTransactionList()
    def makeTransactionList(self):
        for i in range(0, len(self.raw_transaction_list)):
            l = []
            l.append(self.raw_transaction_list[i]['stock_code'])
            l.append(self.raw_transaction_list[i]['stock_number'])
            s = time.strptime(self.raw_transaction_list[i]['buy_date'], "%Y%m%d")
            l.append(time.strftime("%Y-%m-%d", s))
            l.append(self.raw_transaction_list[i]['buy_price'])
            l.append(True)
            self.df.loc[2 * i] = l
            l = []
            l.append(self.raw_transaction_list[i]['stock_code'])
            l.append(self.raw_transaction_list[i]['stock_number'])
            s = time.strptime(self.raw_transaction_list[i]['sell_date'], "%Y%m%d")
            l.append(time.strftime("%Y-%m-%d", s))
            l.append(self.raw_transaction_list[i]['sell_price'])
            l.append(False)
            self.df.loc[2 * i + 1] = l
        self.trading()
    def trading(self):
        for i in range(0, len(self.df)):
            price = 0; # 交易费用
            allTrading = ts.get_hist_data(self.df.loc[i]['stock_code']).sort_index(ascending=True)
            dayTrading = allTrading.loc[allTrading.index == self.df.loc[i]['date']]
            if(self.df.loc[i]['price'] == 1):
                price = dayTrading['open'][0]
            elif(self.df.loc[i]['price'] == 2):
                price = dayTrading['close'][0]
            elif(self.df.loc[i]['price'] == 3):
                price = dayTrading['high'][0]
            else:
                price = dayTrading['low'][0]
            if(self.df.loc[i]['buy'] == True):
                self.buy(self.df.loc[i]['stock_number'], price, self.df.loc[i]['stock_code'])
            else:
                self.sell(self.df.loc[i]['stock_number'], price, self.df.loc[i]['stock_code'])
    def buy(self, number, price, code): # 买入股票
        basicCost = price * number
        additionalCharge1 = basicCost * self.open_tax
        additionalCharge2 = basicCost * self.open_commission if basicCost * self.open_commission > self.min_commission else self.min_commission
        allCost = basicCost + additionalCharge1 + additionalCharge2
        if(self.remaining > allCost):
            self.remaining -= allCost
            print("买入了代码为" + str(code) + '的股票，价格为：' + str(price) + '股数为：' + str(number) + '，可用头寸为：' + str(round(self.remaining, 2)))
        else:
            print('头寸不足，无法交易')
    def sell(self, number, price, code): # 卖出股票
        basicFund = price * number
        charge1 = basicFund * self.open_tax
        charge2 = basicFund * self.open_commission if basicFund * self.open_commission > self.min_commission else self.min_commission
        computedFund = basicFund - charge1 - charge2
        if (self.remaining > computedFund):
            self.remaining += computedFund
            print("卖出了代码为" + str(code) + '的股票，价格为：' + str(price) + '股数为：' + str(number) + '，可用头寸为：' + str(round(self.remaining, 2)))
        else:
            print('头寸不足，无法交易')
    def test(self):
        print(self.df.sort_values(by='date', ascending=True))

if __name__ == '__main__':
    b = [{"stock_code":"000001", "stock_number": 100, "buy_date": "20191203", "buy_price": 1, "sell_date": "20191219",
        "sell_price": 1},
        {"stock_code": "000998", "stock_number": 100, "buy_date": "20191213", "buy_price": 2, "sell_date": "20191230",
        "sell_price": 1},
         {"stock_code": "600004", "stock_number": 100, "buy_date": "20191206", "buy_price": 3, "sell_date": "20200108",
          "sell_price": 4}]
    a = Huice(10000)
    a.set_order_cost(0, 0.005, 0.001, 0.005, 5)
    a.getRawData(b)
    # a.test()