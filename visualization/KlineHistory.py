import pandas as pd
import os
import tushare as ts
from pyecharts.charts import Kline
from pyecharts.charts import Line
import pyecharts.options as opts

tsData = pd.DataFrame()
stockCode = ''

date_list = []
price_list = []
ma5_list = []
ma10_list = []
ma20_list = []

def draw():
    kline = (
        Kline(init_opts=opts.InitOpts(
            width='1800px',
            height='800px',
            page_title=stockCode + '历史K线图',
            js_host="./",
        ))
            .set_global_opts(
            title_opts=opts.TitleOpts(
                title='股票价格走势',
                subtitle=stockCode + '股票价格走势'
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                axis_pointer_type="line"
            ),
            xaxis_opts=opts.AxisOpts(
                # type_="time",
                name='日期',
                split_number=10,
                axispointer_opts=opts.AxisPointerOpts(is_show=True)
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='价格',
                min_=12,
                max_=17,
                split_number=4,
                axispointer_opts=opts.AxisPointerOpts(is_show=True),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                splitarea_opts=opts.SplitAreaOpts(is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1))
            ),
            datazoom_opts=opts.DataZoomOpts(
                range_start=30,
                range_end=70,
            ),
        )
            .add_xaxis(
            xaxis_data=date_list
        )
            .add_yaxis(
            series_name="日K线图",
            is_selected=True,
            y_axis=price_list,
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                    opts.MarkPointItem(type_="min", name="最小值"),
                    opts.MarkPointItem(type_="average", name="平均值")
                ]
            )
        )
    )

    line = (
        Line(init_opts=opts.InitOpts(
            width='1800px',
            height='800px',
            js_host="./",
        ))
        .add_xaxis(
            xaxis_data=date_list
        )
        .add_yaxis(
            series_name="MA5图",
            is_selected=True,
            y_axis=ma5_list,
            label_opts=opts.LabelOpts(is_show=False)
        )
    )

    line2 = (
        Line(init_opts=opts.InitOpts(
            width='1800px',
            height='800px',
            js_host="./",
        ))
            .add_xaxis(
            xaxis_data=date_list
        )
            .add_yaxis(
            series_name="MA10图",
            is_selected=True,
            y_axis=ma10_list,
            label_opts=opts.LabelOpts(is_show=False)
        )
    )

    line3 = (
        Line(init_opts=opts.InitOpts(
            width='1800px',
            height='800px',
            js_host="./",
        ))
            .add_xaxis(
            xaxis_data=date_list
        )
            .add_yaxis(
            series_name="MA20图",
            is_selected=True,
            y_axis=ma20_list,
            label_opts=opts.LabelOpts(is_show=False)
        )
    )

    overlap_kline_line = kline.overlap(line)
    overlap_kline_line = overlap_kline_line.overlap(line2)
    overlap_kline_line = overlap_kline_line.overlap(line3)
    try:
        overlap_kline_line.render(path=stockCode + '-kline.html')
        print('K线图已生成')
    except:
        print('K线图生成失败！')

def change_data(dataframe):
    global date_list, price_list, ma5_list, ma10_list, ma20_list

    # 转成列表
    try:
        for i in range(0, len(dataframe)):
            alist = []
            date_list.append(dataframe['date'].iloc[i])
            # alist.append(tsData['date'].iloc[i])
            alist.append(dataframe['open'].iloc[i])
            alist.append(dataframe['close'].iloc[i])
            alist.append(dataframe['low'].iloc[i])
            alist.append(dataframe['high'].iloc[i])
            ma5_list.append(dataframe['ma5'].iloc[i])
            ma10_list.append(dataframe['ma10'].iloc[i])
            ma20_list.append(dataframe['ma20'].iloc[i])

            price_list.append(alist)
        print('股票数据已成功转换')
        draw()
    except:
        print('股票数据转换失败！')

def date_setting(stock_code, start_date, end_date):
    global tsData, stockCode

    stockCode = stock_code
    tsData = ts.get_hist_data(code=stock_code, start=start_date, end=end_date)
    tsData = tsData.sort_index(ascending=True).reset_index()

    if len(tsData) != 0:
        print('股票数据已成功获取')
        change_data(tsData)
    else:
        print('股票数据获取失败！')

if __name__ == '__main__':
    date_setting(stock_code='000001', start_date='2020-04-01', end_date='2020-09-30')