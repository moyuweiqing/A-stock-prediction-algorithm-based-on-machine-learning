import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import tushare as ts
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM

class LSTM_Predict:
    stock_code = ''
    tsData = pd.DataFrame()

    def __init__(self, stock_code):
        self.stock_code = stock_code
    def date_setting(self, start_date, end_date):
        self.tsData = ts.get_hist_data(code=self.stock_code, start=start_date, end=end_date)
        self.tsData = self.tsData.sort_index(ascending=True).reset_index()
    def makePrediction(self, node):
        # 创建数据框
        new_data = pd.DataFrame(index=range(0, len(self.tsData)), columns=['Date', 'Close'])
        for i in range(0, len(self.tsData)):
            new_data['Date'][i] = self.tsData.index[i]
            new_data['Close'][i] = self.tsData["close"][i]
        # 设置索引
        new_data.index = new_data.Date
        new_data.drop('Date', axis=1, inplace=True)

        # 创建训练集和验证集
        dataset = new_data.values
        print(dataset)
        train = dataset[0:node, :]
        valid = dataset[node:, :]

        # 将数据集转换为x_train和y_train
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(dataset)
        x_train, y_train = [], []
        for i in range(60, len(train)):
            x_train.append(scaled_data[i - 60:i, 0])
            y_train.append(scaled_data[i, 0])
        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

        # 创建和拟合LSTM网络
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
        model.add(LSTM(units=50))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer='adam')
        model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=2)

        # 使用过去值来预测
        inputs = new_data[len(new_data) - len(valid) - 60:].values
        inputs = inputs.reshape(-1, 1)
        inputs = scaler.transform(inputs)
        X_test = []
        for i in range(60, inputs.shape[0]):
            X_test.append(inputs[i - 60:i, 0])
        X_test = np.array(X_test)
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
        closing_price = model.predict(X_test)
        closing_price = scaler.inverse_transform(closing_price)

        # 作图
        train = new_data[:node]
        valid = new_data[node:]
        print('valid长度是：' + str(len(valid)))
        print(len(closing_price))
        valid['Predictions'] = closing_price
        plt.plot(train['Close'], label='训练集')
        plt.plot(valid['Close'], label='真实值')
        plt.plot(valid['Predictions'], label='预测值')
        plt.show()

    def print(self):
        print(self.tsData)

a = LSTM_Predict('000001')
a.date_setting(start_date='2019-05-12', end_date='2019-12-19')
a.makePrediction(130)