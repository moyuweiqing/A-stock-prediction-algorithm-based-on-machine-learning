import pandas as pd
import os
import tushare as ts
from pyecharts.charts import Line
import pyecharts.options as opts

tsData = pd.DataFrame()
date_list = []
open_list = []

def draw():
    line = (
        Line(init_opts=opts.InitOpts(
                                width='2000px',
                                height='800px',
                                page_title = "股票历史曲线图",
                                js_host= "./",
                                ))
            .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=True),
            xaxis_opts=opts.AxisOpts(type_="time"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        )
            .add_xaxis(xaxis_data=date_list)
            .add_yaxis(
            series_name="股市折线图",
            y_axis=open_list,
            symbol="circle",
            is_symbol_show=True,
            is_smooth = True,
            label_opts=opts.LabelOpts(is_show=False),
        )
    )
    line.render(path='first_bar.html')

def date_setting(start_date, end_date):
    global tsData, date_list, open_list

    tsData = ts.get_hist_data(code='000001', start=start_date, end=end_date)
    tsData = tsData.sort_index(ascending=True).reset_index()

    # 转成列表
    for i in range(0, len(tsData)):
        date_list.append(tsData['date'].iloc[i])
        open_list.append(tsData['open'].iloc[i])
    print(date_list)

if __name__ == '__main__':
    date_setting(start_date='2020-04-01', end_date='2020-10-01')
    draw()