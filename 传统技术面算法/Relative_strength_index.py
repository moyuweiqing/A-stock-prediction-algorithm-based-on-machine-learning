import pandas as pd
import tushare as ts

class Relative_strength_index_calculate:
    stock_code = ''
    tsData = pd.DataFrame()
    def __init__(self, stock_code):
        self.stock_code = stock_code
    def date_setting(self, start_date, end_date):
        self.tsData = ts.get_hist_data(code=self.stock_code, start=start_date, end=end_date)
        self.tsData = self.tsData.reset_index()
    def computeRSI(self, day):
        # 获取数据
        data = self.tsData.sort_index(ascending=True, axis=0)
        dataset = data['close']
        RSI_set = []
        # 计算RSI值
        for i in range(0, len(data) - day):
            RSI = 0.0
            bigger_set = 0
            smaller_set = 0
            for j in range(0, 13):
                if dataset[i + j + 1] > dataset[i + j]:
                    bigger_set += dataset[i + j + 1] - dataset[i + j]
                else:
                    smaller_set += dataset[i + j] - dataset[i + j + 1]
            RSI = bigger_set / (bigger_set + smaller_set) * 100
            if i < 5:
                print(bigger_set)
                print(smaller_set)
                print(RSI)
            RSI_set.append(RSI)

        # 定义RSI表格
        dic = {'超买市场（RSI>=80）且实际下跌': 0,
               '超买市场（RSI>=80）但实际上涨': 0,
               '强势市场（50<=RSI<80）且实际下跌': 0,
               '强势市场（50<=RSI<80）但实际上涨': 0,
               '弱式市场（50>RSI>=20）且实际上涨': 0,
               '弱式市场（50>RSI>=20）但实际下跌': 0,
               '超卖市场（RSI<20）且实际上涨': 0,
               '超卖市场（RSI<20）但实际下跌': 0}

        for i in range(0, len(data) - 15):
            if (RSI_set[i] >= 80) & (dataset[i + 15] >= dataset[i + 14]):
                dic['超买市场（RSI>=80）但实际上涨'] += 1
            elif (RSI_set[i] >= 80) & (dataset[i + 15] < dataset[i + 14]):
                dic['超买市场（RSI>=80）且实际下跌'] += 1
            elif (RSI_set[i] < 80) & (RSI_set[i] >= 50) & (dataset[i + 15] >= dataset[i + 14]):
                dic['强势市场（50<=RSI<80）但实际上涨'] += 1
            elif (RSI_set[i] < 80) & (RSI_set[i] >= 50) & (dataset[i + 15] < dataset[i + 14]):
                dic['强势市场（50<=RSI<80）且实际下跌'] += 1
            elif (RSI_set[i] < 50) & (RSI_set[i] >= 20) & (dataset[i + 15] >= dataset[i + 14]):
                dic['弱式市场（50>RSI>=20）且实际上涨'] += 1
            elif (RSI_set[i] < 50) & (RSI_set[i] >= 20) & (dataset[i + 15] < dataset[i + 14]):
                dic['弱式市场（50>RSI>=20）但实际下跌'] += 1
            elif (RSI_set[i] < 20) & (dataset[i + 15] >= dataset[i + 14]):
                dic['超卖市场（RSI<20）且实际上涨'] += 1
            else:
                dic['超卖市场（RSI<20）但实际下跌'] += 1
        print(dic)

a = Relative_strength_index_calculate('000001')
a.date_setting(start_date='2019-05-12', end_date='2019-12-19')
a.computeRSI(14)