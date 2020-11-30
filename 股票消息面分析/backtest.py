import tushare as ts
import pandas as pd
import numpy as np
import time
import draw_line

fund = 0; # 初始资金
remaining = 0; # 头寸
holding = 0; # 持有资金
trading_tax = 0; # 交易费率
hold_stocks = {}; # 持仓股票

date_list = []  # 股票交易日
fund_list = []  # 总资产情况
rate_list = []  # 持有期收益率
buydate_list = ['2020-04-01', '2020-05-06', '2020-06-01', '2020-07-01', '2020-08-03', '2020-09-01', '2020-10-09', '2020-11-02'] # 买入交易日
selldate_list = ['2020-04-30', '2020-05-29', '2020-06-30', '2020-07-31', '2020-08-31', '2020-09-30', '2020-10-30', '2020-11-27']# 卖出交易日

info_table = pd.DataFrame(columns=['股票代码','买入价格','卖出时间','卖出价格','收益率'])
row = 0

buyprice = {}   # 股票代码——买入价

# 设定初始化资金和交易费用
def setting(inputfund, tax):
    global fund, trading_tax, remaining

    fund = inputfund
    remaining = inputfund
    trading_tax = tax

# 持仓股票变化
def holding_stock_exchange(stockcode, number, dir):
    global hold_stocks

    if stockcode not in hold_stocks:
        hold_stocks[stockcode] = 0

    if dir == 'b':
        hold_stocks[stockcode] += number
    else:
        hold_stocks[stockcode] -= number

# 记录买入价
def insert_into_buyprice(stockcode, price):
    global buyprice

    buyprice[stockcode] = price

# 买入流程
def buy(stockcode, date, number, price):
    global remaining, holding, hold_stocks
    basicCost = price * number
    additonalCharge = basicCost * trading_tax
    allCost = basicCost + additonalCharge
    if (remaining > allCost):
        remaining -= allCost
        holding += basicCost
        holding_stock_exchange(stockcode, number, 'b')
        insert_into_buyprice(stockcode, price)
        print("买入了代码为" + str(stockcode) + '的股票，价格为：' + str(price) + '，股数为：' + str(number) + '，可用头寸为：' + str(round(remaining, 2)))
        # print('持仓情况为：', hold_stocks)
    else:
        print('头寸不足，无法交易')

# 卖出流程
def sell(stockcode, date, number, price):
    global remaining, holding, hold_stocks, info_table, row, buyprice

    basicFund = price * number
    charge = basicFund * trading_tax
    computedFund = basicFund - charge

    remaining += computedFund
    holding -= basicFund
    holding_stock_exchange(stockcode, number, 's')

    alist = []
    alist.append(str(stockcode))
    alist.append(buyprice[stockcode])
    alist.append(date)
    alist.append(price)
    alist.append(round((price - buyprice[stockcode]) / buyprice[stockcode], 3))

    info_table.loc[row] = alist
    row += 1

    print("卖出了代码为" + str(stockcode) + '的股票，价格为：' + str(price) + '，股数为：' + str(number) + '，可用头寸为：' + str(round(remaining, 2)))
    # print('持仓情况为：', hold_stocks)

# 交易流程
def trading(stockcode, date, number, price, dir):
    if number == 0:
        return

    if dir == 'b':
        buy(stockcode, date, number, price)
    elif dir == 's':
        sell(stockcode, date, number, price)
    else:
        print('input "dir" error !')

# 记录每日资金情况
def compute_allfund(date):
    global hold_stocks, remaining, fund_list

    total = 0
    for key in hold_stocks.keys():
        if hold_stocks[key] != 0:
            tmp = ts.get_hist_data(key, start=date, end=date)
            tmp = tmp.reset_index(drop=False)
            try:
                total += tmp['close'].iloc[0] * hold_stocks[key]
            except:
                total += buyprice[key]
    total += remaining
    fund_list.append(round(total, 2))
    rate_list.append(round((total - 50000 ) / 50000, 3))
    print('总资产情况为：', total)

# 主函数入口
def main_proc():
    global date_list, hold_stocks, buyprice
    tmp_data = ts.get_hist_data('000001', start='2020-04-01', end='2020-11-27')
    tmp_data = tmp_data.reset_index(drop=False)
    for i in range(0, len(tmp_data)):
        date_list.append(tmp_data['date'].iloc[len(tmp_data) - i - 1])
    print('交易日期为：', date_list)

    # 读入交易文件
    df = pd.read_excel('各月股票队列.xlsx')

    for date in date_list:
        if date in buydate_list:    # 买入日
            print(date, '有买入交易')
            for i in range(0, len(df)):
                if date == str(df['交易时间'].iloc[i])[:10]:
                    stockcode = str(df['股票代码'].iloc[i])
                    while len(stockcode) < 6:
                        stockcode = '0' + stockcode
                    tmp = ts.get_hist_data(stockcode, start=date, end=date)
                    tmp = tmp.reset_index(drop=False)
                    trading(stockcode, date, 100, tmp['close'].iloc[0], 'b')
            compute_allfund(date)
        elif date in selldate_list: # 卖出日
            print(date, '有卖出交易')
            for key in hold_stocks.keys():
                if hold_stocks[key] == 0:
                    continue;
                tmp = ts.get_hist_data(key, start=date, end=date)
                tmp = tmp.reset_index(drop=False)
                try:
                    trading(key, date, hold_stocks[key], tmp['close'].iloc[0], 's')     # 交易日停市
                except:
                    print(key, '日期：', date, '今日停市')
            compute_allfund(date)
        else:
            total = 0
            for key in hold_stocks.keys():
                if hold_stocks[key] != 0:
                    tmp = ts.get_hist_data(key, start=date, end=date)
                    tmp = tmp.reset_index(drop=False)
                    try:
                        if ( tmp['close'].iloc[0] - buyprice[key] ) / buyprice[key] <= -0.05:   # 0.05止损
                            trading(key, date, hold_stocks[key], tmp['close'].iloc[0], 's')
                            print('止损！', date, '股票代码：', key)
                        else:
                            total += tmp['close'].iloc[0] * hold_stocks[key]
                    except:
                        print(key, '日期：', date, '今日停市')
            print(date, '持仓资金为：', round(total, 2))
            compute_allfund(date)

if __name__ == '__main__':
    setting(50000, 0.003)
    main_proc()
    # draw_line.draw(date_list, fund_list, '每日资金情况图')
    draw_line.draw(date_list, rate_list, '持有期收益率情况图')
    info_table.to_csv('个股持有情况分析.csv', encoding='gb18030')