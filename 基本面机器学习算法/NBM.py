# 进行预测
import pandas as pd
import os
import numpy as np
# from fbprophet import Prophet
# import pystan
from sklearn.naive_bayes import GaussianNB

df = pd.read_csv('data2.csv')
print(df['code'].count())
#print(len(df))
p = pd.DataFrame(columns=('code','start', 'predict', 'rate', 'true'))
for i in range(0, df['code'].count()):
    new_data = pd.DataFrame(columns=('ds', 'y'))
    new_data.loc[0] = [df['2017_2'].iloc[i], df['2017_2_roe'].iloc[i]]
    new_data.loc[1] = [df['2017_3'].iloc[i], df['2017_3_roe'].iloc[i]]
    new_data.loc[2] = [df['2018_1'].iloc[i], df['2018_1_roe'].iloc[i]]
    new_data.loc[3] = [df['2018_2'].iloc[i], df['2018_2_roe'].iloc[i]]
    new_data.loc[4] = [df['2018_3'].iloc[i], df['2018_3_roe'].iloc[i]]
    new_data.loc[5] = [df['2019_1'].iloc[i], df['2019_1_roe'].iloc[i]]
    new_data.loc[6] = [df['2019_2'].iloc[i], df['2019_2_roe'].iloc[i]]
    new_data['y'].astype('float')
    code = df['code'].iloc[i]
    true = df['2019_3_true_end'].iloc[i]
    X_list = []
    y_list = []
    x_pre = df['2019_3_start'].iloc[i]
    for j in range(0, 7):
        X_list.append([new_data['y'].iloc[j]])
        y_list.append(new_data['ds'].iloc[j] * 10000)
    X = np.array(X_list)
    Y = np.array(y_list)
    print(X)
    print(Y)
    clf = GaussianNB()
    clf.fit(X, Y.astype('int'))
    rate = clf.predict([[x_pre]])[0] / 10000
    print(rate)
    pre = rate * x_pre

    p.loc[i] = [code, x_pre, pre, rate, true]

p = p.sort_values(by='rate', ascending=False)
# p.to_csv('data3.csv')