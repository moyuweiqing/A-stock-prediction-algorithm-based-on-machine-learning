import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
import os
from fbprophet import Prophet
import pystan

class Prophet_Predict:
    stock_code = ''
    tsData = pd.DataFrame()
    def __init__(self, stock_code):
        self.stock_code = stock_code
    def date_setting(self, start_date, end_date):
        self.tsData = ts.get_hist_data(code=self.stock_code, start=start_date, end=end_date)
        self.tsData = self.tsData.reset_index()
    def makePredictionByDay(self, node): # 按日回测
        new_data = pd.DataFrame(index=range(0, len(self.tsData)), columns=['Date', 'Close'])
        for i in range(0, len(self.tsData)):
            new_data['Date'][i] = self.tsData['date'][i]
            new_data['Close'][i] = self.tsData['close'][i]
        new_data['Date'] = pd.to_datetime(new_data.Date, format='%Y-%m-%d')
        new_data.index = new_data['Date']
        # 准备数据
        new_data = new_data.sort_index(ascending=True)
        new_data.rename(columns={'Close': 'y', 'Date': 'ds'}, inplace=True)
        forecast_valid = []
        # 训练集和预测集
        prediction = new_data[node:]
        for i in range(0, len(new_data) - node):
            train = new_data[:node + i]
            valid = new_data[node + i:]
            # 拟合模型
            model = Prophet()
            model.fit(train)
            # 预测
            close_prices = model.make_future_dataframe(periods=1)
            forecast = model.predict(close_prices)
            forecast_valid.append(forecast['yhat'][len(train):len(train) + 1])
            print(forecast['yhat'][len(train):len(train) + 1])
        prediction['Predictions'] = forecast_valid
        plt.plot(train['y'])
        plt.plot(prediction[['y', 'Predictions']])
        plt.show()
    def makePrediction(self, node): # node为节点天数，在这之前为训练集、之后为测试集，
        new_data = pd.DataFrame(index=range(0, len(self.tsData)), columns=['Date', 'Close'])
        for i in range(0, len(self.tsData)):
            new_data['Date'][i] = self.tsData['date'][i]
            new_data['Close'][i] = self.tsData['close'][i]
        new_data['Date'] = pd.to_datetime(new_data.Date, format='%Y-%m-%d')
        new_data.index = new_data['Date']
        # 准备数据
        new_data = new_data.sort_index(ascending=True)
        new_data.rename(columns={'Close': 'y', 'Date': 'ds'}, inplace=True)
        forecast_valid = []
        # 训练集和预测集
        train = new_data[:node]
        valid = new_data[node:]
        # 拟合模型
        model = Prophet()
        model.fit(train)
        # 预测
        close_prices = model.make_future_dataframe(periods=len(valid))
        forecast = model.predict(close_prices)
        forecast_valid = forecast['yhat'][node:]
        # 画图
        valid['Predictions'] = forecast_valid.values
        plt.plot(train['y'], label = '训练集')
        plt.plot(valid[['y', 'Predictions']], label = ['真实值', '预测值'])
        plt.show()

a = Prophet_Predict('000001')
a.date_setting(start_date='2019-05-12', end_date='2019-12-19')
a.makePrediction(100)