import pandas as pd
import tushare as ts
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score,accuracy_score,roc_auc_score
from sklearn.ensemble import RandomForestClassifier #随机森林分类模型


class RF_predict:
    stock_code = ''
    tsData = pd.DataFrame()
    def __init__(self, stock_code):
        self.stock_code = stock_code
    def date_setting(self, start_date, end_date):
        self.tsData = ts.get_hist_data(code=self.stock_code, start=start_date, end=end_date)
        self.tsData = self.tsData.reset_index()
        # print(self.tsData)
    def make_predict(self, node):
        self.tsData["(t+1)-(t)"] = self.tsData['close'] - self.tsData['close'].shift(-1)
        self.tsData['label'] = 0
        # 构建对应表
        for i in range(0, len(self.tsData)):
            if self.tsData["(t+1)-(t)"].loc[i] > 0:
                self.tsData['label'].loc[i] = 1
            else:
                self.tsData['label'].loc[i] = 0

        # 构建数据集
        test_data = self.tsData[: len(self.tsData) - node]
        train_data = self.tsData[len(self.tsData) - node : ]
        train_X = train_data.ix[:, 'open': 'close'].values
        train_y = train_data['label'].values
        test_X = test_data.ix[:, 'open': 'close'].values
        test_y = test_data['label'].values

        # 进行预测
        clf = RandomForestClassifier(max_depth=1, n_estimators=20)
        clf.fit(train_X, train_y)
        print(accuracy_score(train_y, clf.predict(train_X)))
        print(accuracy_score(test_y, clf.predict(test_X)))
        print(roc_auc_score(test_y,clf.predict(test_X))) # 召回率

a = RF_predict('000001')
a.date_setting(start_date='2019-05-12', end_date='2019-12-19')
a.make_predict(140)