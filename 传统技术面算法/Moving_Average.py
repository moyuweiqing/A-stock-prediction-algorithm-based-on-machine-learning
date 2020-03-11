import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt

from pylab import * #改变plot字体，适应中文
mpl.rcParams['font.sans-serif'] = ['SimHei']

class Moving_Average_Predict:
    stock_code = ''
    tsData = pd.DataFrame()
    def __init__(self, stock_code):
        self.stock_code = stock_code
    def date_setting(self, start_date, end_date):
        self.tsData = ts.get_hist_data(code=self.stock_code, start=start_date, end=end_date)
        self.tsData = self.tsData.reset_index()
    def make_predict(self, day): # day为窗口大小
        new_data = pd.DataFrame(index=range(0, len(self.tsData)), columns=['date', 'close'])
        for i in range(0, len(self.tsData)):  # 使用收盘价进行处理
            new_data['date'][i] = self.tsData.index[i]
            new_data['close'][i] = self.tsData["close"][len(self.tsData) - i - 1]
        new_data = new_data.sort_index(ascending=True)
        # 划定
        train = new_data[:len(self.tsData) - day]
        valid = new_data[len(self.tsData) - day:]
        # 做出预测
        preds = []
        for i in range(0, day):
            a = train['close'][len(train) - day + i:].sum() + sum(preds)
            b = a / day
            preds.append(b)
        # 画图
        valid['Predictions'] = 0
        valid['Predictions'] = preds
        plt.plot(train['close'], label=u'训练集')
        plt.plot(valid['Predictions'], label=u'预测值')
        plt.plot(valid['close'], label=u'真实值')
        plt.show()

a = Moving_Average_Predict('000001')
a.date_setting(start_date='2019-05-12', end_date='2019-12-19')
a.make_predict(15)