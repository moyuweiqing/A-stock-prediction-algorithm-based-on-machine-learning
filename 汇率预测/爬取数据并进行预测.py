from bs4 import BeautifulSoup
import requests
import csv
import os
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM
import tensorflow as tf
from pyecharts.charts import Line
from pyecharts.charts import Grid
import pyecharts.options as opts
import time

header = ['日期','中行汇买价','中行钞买价','中行钞卖价', '央行中间价']
page_count = 57

def get_page_resp(page_number=1, startdate="2010-09-15", enddate="2020-12-01", money_code="USD"):
    params = {
        "startdate": startdate,
        "enddate": enddate,
        "money_code": money_code,
        "page": page_number
    }
    base_url = "http://biz.finance.sina.com.cn/forex/forex.php"
    r = requests.get(base_url, params=params)
    r.encoding = "GB2312"
    return r

def get_bs4_table_elem(response):
    soup = BeautifulSoup(response.text,'html.parser')
    return soup.find(id="data_table").table

def parse():
    with open("data.csv", "w", encoding="utf-8", newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(header)
        for page_number in range(1, page_count + 1):
            table = get_bs4_table_elem(get_page_resp(page_number))
            for idx, tr in enumerate(table.find_all("tr")):
                if idx == 0:
                    continue
                csv_writer.writerow([td.text.strip() for td in tr.find_all("td")])

def draw(datelist, pricelist1, pricelist2, title):
    min_value = min(pricelist1, pricelist2)
    max_value = max(pricelist1, pricelist2)

    line = (
        Line(init_opts=opts.InitOpts(
            width='1800px',
            height='800px',
            js_host="./",
        ))
            .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
            ),
            legend_opts=opts.LegendOpts(
                is_show=True,
                pos_top=10,
                pos_left="center",
                item_width=30,
                item_height=15,
                textstyle_opts=opts.TextStyleOpts(
                    font_family='Microsoft Yahei',
                    font_size=14,
                    font_style='oblique'
                )
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="cross",
                background_color="rgba(245, 245, 245, 0.8)",
                border_width=1,
                border_color="#ccc",
                textstyle_opts=opts.TextStyleOpts(color="#000"),
            ),
            xaxis_opts=opts.AxisOpts(
                # type_="time",
                name='日期',
                split_number=10,
                name_gap=35,
                axispointer_opts=opts.AxisPointerOpts(is_show=True),
                name_textstyle_opts=opts.TextStyleOpts(
                    font_size=16,
                    font_family='Microsoft Yahei'
                )
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                min_=min_value,
                max_=max_value,
                split_number=4,
                axispointer_opts=opts.AxisPointerOpts(is_show=True),
                name_textstyle_opts=opts.TextStyleOpts(
                    font_size=16,
                    font_family='Microsoft Yahei'
                ),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                splitarea_opts=opts.SplitAreaOpts(is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1))
            ),
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True,
                link=[{"xAxisIndex": "all"}],
                label=opts.LabelOpts(background_color="#777"),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False,
                    type_="inside",
                    # xaxis_index=[0, 1],
                    range_start=30,
                    range_end=70,
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    # xaxis_index=[0, 1],
                    type_="slider",
                    pos_top="96%",
                    range_start=38,
                    range_end=70,
                ),
            ],
        )
            .add_xaxis(xaxis_data=datelist)
            .add_yaxis(series_name="实际值",
                       is_selected=True,
                       y_axis=pricelist1,
                       label_opts=opts.LabelOpts(is_show=False)
            )
            .add_yaxis(series_name="预测值",
                       is_selected=True,
                       y_axis=pricelist2,
                       label_opts=opts.LabelOpts(is_show=False)
            )
            .render(title + '.html')
    )

def process(filename, columnname, timsteps=60, node=0.2, precision = 2, savename = 'test'):
    # 获取数据
    path = os.path.abspath("./")
    path = path + '/' + filename
    df = pd.read_csv(path)
    df.index = df['日期']
    df = df.sort_index(ascending=True, axis=0)
    # 创建数据框
    new_data = pd.DataFrame(index=range(0,len(df)),columns=['Date', 'Close'])
    for i in range(0,len(df)):
        new_data['Date'][i] = df.index[i]
        new_data['Close'][i] = df[columnname][i]

    # 设置索引
    new_data.index = new_data.Date
    new_data.drop('Date', axis=1, inplace=True)
    node = int (node * len(new_data))

    # 创建训练集和验证集
    dataset = new_data.values

    # 设定训练集和测试集的分隔
    train = dataset[0:node,:]
    valid = dataset[node:,:]

    # 数据归一化处理
    # 将数据集转换为x_train和y_train
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset)

    # 划定预测情况，用前n天的数据预测第n+1天的数据
    x_train, y_train = [], []
    for i in range(timsteps,len(train)):
        x_train.append(scaled_data[i-timsteps:i,0])
        y_train.append(scaled_data[i,0])

    # 三维数组化
    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))

    # 创建和拟合LSTM网络
    model = Sequential()

    # LSTM层
    model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1],1)))
    # Dropout层，随机删除20%的数据
    model.add(Dropout(.2))
    # LSTM层
    model.add(LSTM(units=50, return_sequences=False))
    # Dropout层
    model.add(Dropout(.2))
    # 全连接层
    model.add(Dense(1))

    # 模型编译
    model.compile(loss='mean_squared_error', optimizer='adam')
    # 模型拟合
    model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=2)

    # 使用过去值来预测
    # 测试集
    inputs = new_data[len(new_data) - len(valid) - timsteps:].values
    inputs = inputs.reshape(-1,1)
    inputs  = scaler.transform(inputs)

    # 测试集，同样的道理
    X_test = []
    for i in range(60,inputs.shape[0]):
        X_test.append(inputs[i-timsteps:i,0])
    X_test = np.array(X_test)

    X_test = np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))
    # 模型预测
    closing_price = model.predict(X_test)
    closing_price = scaler.inverse_transform(closing_price)

    # 模型均方根值
    rms = np.sqrt(np.mean(np.power((valid-closing_price),2)))
    print(rms)

    valid = new_data[node:]
    valid['Predictions'] = closing_price

    # 图表
    train = new_data[:node]
    valid = new_data[node:]
    train.to_csv(savename + 'train.csv')
    valid['Predictions'] = closing_price
    valid.to_csv(savename + 'valid.csv')

    datelist = []
    pricelist1 = []
    pricelist2 = []
    for i in range(0, len(train)):
        datelist.append(train.index.tolist()[i])
        pricelist1.append(train['Close'].iloc[i])
        pricelist2.append(train['Close'].iloc[i])
    for i in range(0, len(valid)):
        datelist.append(valid.index.tolist()[i])
        pricelist1.append(float(valid['Close'].iloc[i]))
        pricelist2.append(round(float(valid['Predictions'].iloc[i]), precision))
    draw(datelist, pricelist1, pricelist2, savename)

def process2(filename, columnname, timsteps=60, node=0.2, precision = 2, savename = 'test'):
    # 获取数据
    path = os.path.abspath("./")
    path = path + '/' + filename
    data = pd.read_csv(path)
    data = data.sort_index(ascending=False, axis=0)
    print(data.head())
    node = int(node * len(data))

    train = data[columnname].iloc[:node].values
    valid = data[columnname].iloc[node:].values

    model = auto_arima(train, start_p=1, start_q=1, max_p=2, max_q=2, m=12, start_P=0, seasonal=True, d=1, D=1,
                       trace=True, error_action='ignore', suppress_warnings=True)

    model.fit(train)
    # 进行预测
    forecast = model.predict(n_periods=len(valid))
    # forecast = pd.DataFrame(forecast, columns=['Prediction'])

    #
    datelist = []
    pricelist1 = []
    pricelist2 = []
    for i in data['日期']:
        datelist.append(i)
    for i in train:
        pricelist1.append(i)
        pricelist2.append(i)
    for i in valid:
        pricelist1.append(i)
    for i in forecast:
        pricelist2.append(i)

    draw(datelist, pricelist1, pricelist2, savename)

if __name__ == '__main__':
    # 爬取数据
    parse()
    time.sleep(2)

    # LSTM预测日数据
    process(filename='data.csv', columnname='中行汇买价', timsteps=60, node=0.2, precision=2, savename = '日预测图')

    # 将每分钟的数据处理成每小时的数据
    filelist = ['DAT_XLSX_GBPUSD_M1_202009.xlsx', 'DAT_XLSX_GBPUSD_M1_202010.xlsx', 'DAT_XLSX_GBPUSD_M1_202011.xlsx']
    day_df = pd.DataFrame(columns=['日期', '开盘价', '最高价', '最低价', '收盘价'])
    row = 0
    for f in filelist:
        df = pd.read_excel(f)
        for i in range(0, len(df), 60):
            alist = []
            alist.append(df['时间'].iloc[i])
            alist.append(df['开盘价'].iloc[i])
            alist.append(df['最高价'].iloc[i])
            alist.append(df['最低价'].iloc[i])
            alist.append(df['收盘价'].iloc[i])
            day_df.loc[row] = alist
            row += 1
    day_df.index = day_df.日期
    day_df.drop('日期', axis=1, inplace=True)
    day_df.to_csv('每时数据.csv')

    # LSTM对每小时的数据进行预测
    process(filename='每时数据.csv', columnname='开盘价', timsteps=60, node=0.2, precision=5, savename='小时预测图')

    # ARIMA对每日数据进行预测
    process(filename='data.csv', columnname='中行汇买价', timsteps=60, node=0.8, precision=2, savename='日预测图ARIMA')