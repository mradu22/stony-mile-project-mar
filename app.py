from flask import Flask, render_template, request, redirect
import pandas as pd
from pandas import DataFrame,Series
import requests
import datetime as dt
import bokeh
from bokeh.plotting import figure, show, output_file
from bokeh.palettes import Dark2_5 as palette
from bokeh.embed import components
import os


apiKey='dtw577q6gxFchMvnz5fj'

def get_stock(ticker, apiKey) :

    ticker = ticker.upper()
    now = dt.datetime.now().date()
    then = now - dt.timedelta(days=90)
    then = "&start_date=" + then.strftime("%Y-%m-%d")
    now  = "&end_date=" + now.strftime("%Y-%m-%d")

    UrlRequest = 'https://www.quandl.com/api/v3/datasets/WIKI/' + ticker + \
                    '.json?api_key=' + apiKey + now + then

    print(UrlRequest)

    r = requests.get(UrlRequest)

    if r.status_code < 400 :
        name = r.json()['dataset']['name']
        name = name.split('(')[0]

        dat = r.json()['dataset']
        df = DataFrame(dat['data'], columns=dat['column_names'] )
        df = df.set_index(pd.DatetimeIndex(df['Date']))
    else :
        print("Cannot find stock")
        df = None
        name = None

    return df, name


def PlotStock(df, priceReq, tickerText ):

    plot_title = tickerText + " Prices"
    p = figure(x_axis_type="datetime", width=800, height=600,title=plot_title)

    if type(priceReq) == list :
        for req, color in zip(priceReq,palette):
            p.line(df.index, df[req], legend=req, line_width=1,color=color)
    else :
        p.line(df.index, df[priceReq], legend=priceReq, line_width=1)

    p.grid.grid_line_alpha=0.3
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    p.legend.orientation = "horizontal"

    if 0:
        bokeh.io.output_file('templates/plotstock.html')
        bokeh.io.save(p)

    script, div = components(p)
    return script, div



app = Flask(__name__)

app.vars = {}
app.vars['apiKey'] = apiKey

@app.route('/')
def main():
    return redirect('/index')

@app.route('/index', methods=['GET','POST'])
def index():
    return render_template('index.html')


@app.route('/plotpage', methods=['POST'])
def plotpage():
    tickStr = request.form['tickerText'] #gets the ticker NAME (GOOG)
    reqList = request.form.getlist('priceCheck') #gets the stock feature (High,Low,Close..)

    print('tickStr is {} and reqList is {} and type(reqList) is {}'.format(tickStr,reqList,type(reqList)))
    #print('type of tickfeat {} and value:{}'.format(type(tickFeat),ticFeat))

    app.vars['ticker'] = tickStr.upper()   #defines ticker name as an app var (ticker)
    app.vars['priceReqs'] = reqList  #defines the stock feature as an app var (priceReqs)

    df,name = get_stock(app.vars['ticker'], app.vars['apiKey'])

    print('tickStr is {} and reqList is {}'.format(app.vars['ticker'],app.vars['priceReqs']))

    # if the stock ticker isn't valid, reload with warning message
    if not type(df) == DataFrame :
        msg = "Stock does not exist."
        return render_template('index.html', msg=msg)
    else:
        script, div = PlotStock(df, app.vars['priceReqs'], app.vars['ticker'])
        return render_template('plot.html', script=script, div=div, ticker=name)


if __name__ == '__main__':
    port=int(os.environ.get("PORT",5005))

    if port==5005 :
        app.run(port=port,host='0.0.0.0')
    else :
        app.run(port=port)
