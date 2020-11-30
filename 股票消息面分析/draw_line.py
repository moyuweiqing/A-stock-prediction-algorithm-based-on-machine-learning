import pandas as pd
import os
import tushare as ts
from pyecharts.charts import Line
from pyecharts.charts import Grid
import pyecharts.options as opts

def draw(datelist, pricelist, title):
    min_value = min(pricelist)
    max_value = max(pricelist)
    
    line = (
        Line(init_opts=opts.InitOpts(
            width='1800px',
            height='800px',
            js_host="./",
        ))
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                # subtitle='股票价格走势'
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
                # name='价格',
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
        .add_yaxis(series_name="走势情况",
            is_selected=True,
            y_axis=pricelist,
            label_opts=opts.LabelOpts(is_show=False)
        )
        .render(title + '.html')
    )