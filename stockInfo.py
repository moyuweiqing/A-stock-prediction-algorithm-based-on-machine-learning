import pandas as pd
import os
import tushare as ts
from pyecharts.charts import Kline
from pyecharts.charts import Line
import pyecharts.options as opts

tsData = pd.DataFrame()
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
            page_title="股票历史曲线图",
            js_host="./",
        ))
            .set_global_opts(
            title_opts=opts.TitleOpts(
                title='股票价格走势',
                subtitle='000001股票价格走势'
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                axis_pointer_type="line"
            ),
            xaxis_opts=opts.AxisOpts(
                # type_="time",
                name='日期',
                split_number=10
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='价格',
                min_=12,
                max_=17,
                split_number=4,
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
            series_name="股市K线图",
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
            page_title="股票历史曲线图",
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
            page_title="股票历史曲线图",
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
            page_title="股票历史曲线图",
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
    overlap_kline_line.render(path='first_bar.html')


def date_setting(start_date, end_date):
    global tsData, date_list, price_list, ma5_list, ma10_list, ma20_list

    tsData = ts.get_hist_data(code='000001', start=start_date, end=end_date)
    tsData = tsData.sort_index(ascending=True).reset_index()

    # 转成列表
    for i in range(0, len(tsData)):
        alist = []
        date_list.append(tsData['date'].iloc[i])
        # alist.append(tsData['date'].iloc[i])
        alist.append(tsData['open'].iloc[i])
        alist.append(tsData['close'].iloc[i])
        alist.append(tsData['low'].iloc[i])
        alist.append(tsData['high'].iloc[i])
        ma5_list.append(tsData['ma5'].iloc[i])
        ma10_list.append(tsData['ma10'].iloc[i])
        ma20_list.append(tsData['ma20'].iloc[i])

        price_list.append(alist)

if __name__ == '__main__':
    date_setting(start_date='2020-04-01', end_date='2020-09-30')
    draw()
