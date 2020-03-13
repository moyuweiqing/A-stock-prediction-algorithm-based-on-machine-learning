import pandas as pd
from sklearn import svm,preprocessing
import tushare as ts

class SVM_Predict:
    stock_code = ''
    tsData = pd.DataFrame()
    def __init__(self, stock_code):
        self.stock_code = stock_code
    def date_setting(self, start_date, end_date):
        self.tsData = ts.get_hist_data(code=self.stock_code, start=start_date, end=end_date)
        self.tsData = self.tsData.reset_index()
    def makeSVMPrediction(self, rate): # rate表示训练集和测试集的比例
        df_CB = self.tsData.sort_index(ascending=True, axis=0)
        df_CB = df_CB.set_index('date')
        df_CB = df_CB.sort_index()
        # value表示涨跌, =1为涨，=0为跌
        value = pd.Series(df_CB['close'] - df_CB['close'].shift(1), \
                          index=df_CB.index)
        value = value.bfill()
        value[value >= 0] = 1
        value[value < 0] = 0
        df_CB['Value'] = value
        # 后向填充空缺值
        df_CB = df_CB.fillna(method='bfill')
        df_CB = df_CB.astype('float64')
        print(df_CB.head())

        L = len(df_CB)
        train = int(L * rate)
        total_predict_data = L - train

        # 对样本特征进行归一化处理
        df_CB_X = df_CB.drop(['Value'], axis=1)
        df_CB_X = preprocessing.scale(df_CB_X)

        # 开始循环预测，每次向前预测一个值
        correct = 0
        train_original = train
        while train < L:
            Data_train = df_CB_X[train - train_original:train]
            value_train = value[train - train_original:train]
            Data_predict = df_CB_X[train:train + 1]
            value_real = value[train:train + 1]

            # 核函数分别选取'ploy','linear','rbf'
            # classifier = svm.SVC(C=1.0, kernel='poly')
            # classifier = svm.SVC(kernel='linear')
            classifier = svm.SVC(C=1.0, kernel='rbf')
            classifier.fit(Data_train, value_train)
            value_predict = classifier.predict(Data_predict)
            print("value_real=%d value_predict=%d" % (value_real[0], value_predict))
            # 计算测试集中的正确率
            if (value_real[0] == int(value_predict)):
                correct = correct + 1
            train = train + 1
        print(correct)
        print(total_predict_data)
        correct = correct * 100 / total_predict_data
        print("Correct=%.2f%%" % correct)

a = SVM_Predict('000001')
a.date_setting(start_date='2019-05-12', end_date='2019-12-19')
a.makeSVMPrediction(0.8)