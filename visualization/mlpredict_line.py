import pyecharts.options as opts
from pyecharts.charts import Line
from pmdarima import auto_arima
import tushare as ts
import pandas as pd

stockCode = ''
date_list = []
predict_list = []
raw_list = []
day_predict_list = []

minvalue = 0
maxvalue = 0

def draw():
    (
        Line(init_opts=opts.InitOpts(
                width='1800px',
                height='800px',
                js_host="./",
            ))
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title='股票价格走势预测',
                subtitle=stockCode + '股票价格走势预测'
            ),
            legend_opts=opts.LegendOpts(
                is_show=True,  # 显示图例
                pos_top=10,  # 离上边的像素值
                pos_left="center",  # 居中
                item_width=30,  # 图例宽度
                item_height=15,  # 图例高度
                textstyle_opts=opts.TextStyleOpts(  # 字体样式
                    font_family='Microsoft Yahei',  # 微软雅黑
                    font_size=14,  # 字体大小
                    font_style='oblique'  # 倾斜
                )
            ),
            tooltip_opts=opts.TooltipOpts(  # 提示框设置
                trigger="axis",  # 坐标轴触发
                axis_pointer_type="cross",  # 正交十字准星指示器
                background_color="rgba(245, 245, 245, 0.8)",  # 提示框浮层背景颜色
                border_width=1,  # 提示框边界宽度
                border_color="#ccc",  # 提示框边界颜色
                textstyle_opts=opts.TextStyleOpts(color="#000"),  # 提示框字体样式
            ),
            xaxis_opts=opts.AxisOpts(  # x轴设置
                # type_="time",
                name='日期',  # 坐标轴名称
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
                name='价格',
                min_=int(minvalue) - 2,
                max_=int(maxvalue) + 2,
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
            datazoom_opts=opts.DataZoomOpts(
                is_show=True,
                # xaxis_index=[0, 1],
                type_="slider",
                # pos_top="92%",
                range_start=40,
                range_end=70,
            )
        )
        .add_xaxis(xaxis_data=date_list)
        .add_yaxis(
            series_name="预测值",
            y_axis=predict_list,
            symbol="emptyCircle",
            is_symbol_show=True,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="实际值",
            y_axis=raw_list,
            symbol="emptyCircle",
            is_symbol_show=True,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="逐日预测值",
            y_axis=day_predict_list,
            symbol="emptyCircle",
            is_symbol_show=True,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .render(stockCode + "-mlpredict.html")
    )

def predict(stock_code, start_date, end_date, node):
    global predict_list, raw_list, stockCode
    global minvalue, maxvalue

    stockCode = stock_code
    tsData = ts.get_hist_data(code=stock_code, start=start_date, end=end_date)
    tsData = tsData.sort_index(ascending=True).reset_index()

    train = tsData['close'].iloc[:node].values
    valid = tsData['close'].iloc[node:].values

    model = auto_arima(train, start_p=1, start_q=1, max_p=2, max_q=2, m=12, start_P=0, seasonal=True, d=1, D=1,
                       trace=True, error_action='ignore', suppress_warnings=True)

    model.fit(train)
    # 进行预测
    forecast = model.predict(n_periods=len(valid))

    for i in range(0, len(tsData)):
        date_list.append(tsData['date'].iloc[i])
        raw_list.append(tsData['close'].iloc[i])

    for i in range(0, node):
        predict_list.append(tsData['close'].iloc[i])
    for i in range(0, len(valid)):
        predict_list.append(forecast[i])

    minvalue = min(min(predict_list), min(raw_list))
    maxvalue = max(max(predict_list), max(raw_list))

def day_predict(stock_code, start_date, end_date, node):
    global day_predict_list

    tsData = ts.get_hist_data(code=stock_code, start=start_date, end=end_date)
    tsData = tsData.sort_index(ascending=True).reset_index()

    train = tsData['close'].iloc[:node].values
    valid = tsData['close'].iloc[node:].values

    for i in range(0, node):
        day_predict_list.append(tsData['close'].iloc[i])

    for day in range(0, len(tsData) - node):
        train = tsData['close'].iloc[:node + day].values
        valid = tsData['close'].iloc[node + day:].values

        model = auto_arima(train, start_p=1, start_q=1, max_p=2, max_q=2, m=12, start_P=0, seasonal=True, d=1, D=1,
                           trace=True, error_action='ignore', suppress_warnings=True)

        model.fit(train)
        # 进行预测
        forecast = model.predict(n_periods=1)
        day_predict_list.append(forecast[0])

if __name__ == '__main__':
    predict(stock_code='000001', start_date='2020-04-01', end_date='2020-09-30', node=100)
    day_predict(stock_code='000001', start_date='2020-04-01', end_date='2020-09-30', node=100)
    draw()