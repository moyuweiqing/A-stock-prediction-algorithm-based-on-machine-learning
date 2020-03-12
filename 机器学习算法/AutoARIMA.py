# 自回归积分滑动平均模型
import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
from pmdarima import auto_arima

class AutoARIMA_pridict:
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
        forecast = []
        # 训练集和预测集
        prediction = new_data[node:]
        for i in range(0, len(new_data) - node):
            train = new_data[:node + i]
            valid = new_data[node + i:]
            # 对收盘价进行测试
            training = train['Close']
            validation = valid['Close']
            # 拟合模型
            model = auto_arima(training, start_p=1, start_q=1, max_p=2, max_q=2, m=12, start_P=0, seasonal=True, d=1,
                               D=1,
                               trace=True, error_action='ignore', suppress_warnings=True)  #
            model.fit(training)
            # 预测
            forecast.append(model.predict(n_periods=1)[0])
        prediction['Prediction'] = forecast
        plt.plot(train['Close'])
        plt.plot(prediction[['Close', 'Prediction']])
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
        # 训练集和预测集
        train = new_data[:node]
        valid = new_data[node:]
        # 对收盘价进行测试
        training = train['Close']
        validation = valid['Close']
        # 拟合模型
        model = auto_arima(training, start_p=1, start_q=1, max_p=2, max_q=2, m=12, start_P=0, seasonal=True, d=1, D=1,
                           trace=True, error_action='ignore', suppress_warnings=True)#
        model.fit(training)
        # 进行预测
        forecast = model.predict(n_periods=len(valid))
        forecast = pd.DataFrame(forecast, index=valid.index, columns=['Prediction'])
        # 画图
        valid['Predictions'] = forecast['Prediction']
        plt.plot(train['Close'], label = '训练集')
        plt.plot(valid[['Close', 'Predictions']], label = ['真实值', '预测值'])
        plt.show()

a = AutoARIMA_pridict('000001')
a.date_setting(start_date='2019-05-12', end_date='2019-12-19')
a.makePredictionByDay(140)