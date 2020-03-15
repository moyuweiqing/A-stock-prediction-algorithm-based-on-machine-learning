import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
from sklearn import neighbors
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))

class kNN_pridict:
    stock_code = ''
    tsData = pd.DataFrame()
    def __init__(self, stock_code):
        self.stock_code = stock_code
    def date_setting(self, start_date, end_date):
        self.tsData = ts.get_hist_data(code=self.stock_code, start=start_date, end=end_date)
        self.tsData = self.tsData.reset_index()
    def makePrediction(self, node): # node为节点天数，在这之前为训练集、之后为测试集
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
        x_train = train.drop('Close', axis=1)
        y_train = train['Close']
        x_valid = valid.drop('Close', axis=1)
        y_valid = valid['Close']
        # 缩放数据
        x_train_scaled = scaler.fit_transform(x_train)
        x_train = pd.DataFrame(x_train_scaled)
        x_valid_scaled = scaler.fit_transform(x_valid)
        x_valid = pd.DataFrame(x_valid_scaled)
        # 使用gridsearch查找最佳参数
        params = {'n_neighbors': [2, 3, 4, 5, 6, 7, 8, 9]}
        knn = neighbors.KNeighborsRegressor()
        model = GridSearchCV(knn, params, cv=5)
        # 拟合模型并进行预测
        model.fit(x_train, y_train)
        preds = model.predict(x_valid)
        # 画图
        valid['Predictions'] = 0
        valid['Predictions'] = preds
        plt.plot(valid[['Close', 'Predictions']])
        plt.plot(train['Close'])
        plt.show()

a = kNN_pridict('000001')
a.date_setting(start_date='2019-05-12', end_date='2019-12-19')
a.makePrediction(140)