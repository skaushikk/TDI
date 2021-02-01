from flask import Flask, render_template, request
from bokeh.plotting import figure, show
from bokeh.embed import file_html, components
from bokeh.resources import CDN
from bokeh.embed import components, file_html
from bokeh.resources import CDN
from flask import Flask, render_template, request, redirect
import numpy as np
import requests
import json
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta, date
from bokeh.plotting import figure, show, output_file
from bokeh.models import CustomJS, ColumnDataSource, HoverTool, Slider, DateSlider, DateRangeSlider
from bokeh.layouts import column
import numpy as np

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


# @app.route('/static')
# def plot():
#     x = np.random.random(100) * 10
#     y = np.random.random(100) * 10
#     s = np.random.random(100)
#
#     p = figure(width=300, height=300)
#     p.circle(x, y, radius=s, fill_alpha=0.6)

# return file_html(p, CDN)

@app.route('/plot2')
def plot2():
    ticker = str(request.args.get('ticker', 100))

    key = '1GD3M7E7LM0ERP3K'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&outputsize=full&apikey={key}'
    response = requests.get(url)
    dat = response.json()

    metadata = dat["Meta Data"]
    key_dat = list(dat.keys())[1]  # ugly
    ts = dat[key_dat]
    df = pd.DataFrame(ts).T
    df.columns = ['open', 'high', 'low', 'close', 'close_adjusted', 'volume', 'div_amount', 'split_coeff']
    df.index = pd.to_datetime(df.index)
    df.index.name = 'timestamp'

    df = df.reset_index()

    start = df.iloc[-1].timestamp
    delta = timedelta(days=30)
    end = df.iloc[0].timestamp

    # output to static HTML file
    # output_file('file.html')

    TOOLS = 'crosshair, pan, wheel_zoom, box_zoom, reset, tap, save, box_select, poly_select, lasso_select'
    p = figure(tools=TOOLS, x_axis_type='datetime', x_axis_label='Time', y_axis_label='close price',
               x_range=(start, end), height=500, width=1000)

    hover = HoverTool(
        tooltips=[("Date", "@timestamp{%F}"),
                  ("Open", "@open{$0,0.00}"),
                  ("Close", "@close_adjusted{$0,0.00}"),
                  ("Volume", "@volume{(0 a)}")],
        formatters={'@timestamp': 'datetime'})

    x = df.timestamp.values
    y = df.close_adjusted.values

    r = p.line(x='timestamp', y='close_adjusted', source=df, color="#1234aa", line_width=1)
    p.add_tools(hover)

    b = p.rect(x='timestamp', y='volume', width=0.4, color="#CAB2D6")

    script, div = components(p)

    return render_template('plot2.html',
                           script=script, div=div)


if __name__ == '__main__':
    app.run(port=8008, debug=True)