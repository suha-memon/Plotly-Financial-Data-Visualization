import pandas as pd
import plotly.graph_objects as go
import datetime
import numpy as np

from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries


class Plot:
    def __init__(self):
        self.api_key = 'REPLACE_THIS_WITH_YOUR_16_CHARACTER_API_KEY'

        # Alpha Vantage initialize Time Series and Technical Indicators
        self.ts = TimeSeries(key=self.api_key, output_format='pandas')  # Time series
        self.ti = TechIndicators(key=self.api_key, output_format='pandas')  # Technical indicators

    def full_plot(self, ticker):
        # Choose Ticker, Start Date, and periods
        start_date = '2023-01-03'
        first_ema_period = 8
        second_ema_period = 21
        sma_period = 10
        rsi_period = 14
        interval = 'daily'
        series_type = 'close'

        # Alpha Vantage retrieve data
        data_daily, meta_data_ts = self.ts.get_daily(ticker,
                                                     outputsize='full')  # pylint: disable=unbalanced-tuple-unpacking
        sar_daily, meta_sar = self.ti.get_sar(ticker, interval=interval)  # pylint: disable=unbalanced-tuple-unpacking
        macd_daily, meta_macd = self.ti.get_macd(ticker, interval=interval,
                                                 series_type=series_type)  # pylint: disable=unbalanced-tuple-unpacking
        ema_daily8, meta_ema = self.ti.get_ema(ticker, interval=interval, time_period=first_ema_period,
                                               series_type=series_type)  # pylint: disable=unbalanced-tuple-unpacking
        ema_daily21, meta_ema = self.ti.get_ema(ticker, interval=interval, time_period=second_ema_period,
                                                series_type=series_type)  # pylint: disable=unbalanced-tuple-unpacking
        sma_daily, meta_sma = self.ti.get_sma(ticker, interval=interval, time_period=sma_period,
                                              series_type=series_type)  # pylint: disable=unbalanced-tuple-unpacking
        rsi_daily, meta_rsi = self.ti.get_rsi(ticker, interval=interval, time_period=rsi_period,
                                              series_type=series_type)  # pylint: disable=unbalanced-tuple-unpacking

        # Renaming daily data
        data_daily.rename(index=pd.to_datetime, columns=lambda x: x.split(' ')[-1], inplace=True)

        # Current Date and Time
        cur_dt = datetime.datetime.now()
        dt_str = cur_dt.strftime('%Y-%m-%d')

        # Setting dates for data
        df_daily = data_daily[start_date:dt_str]

        # Converting data into dataframes
        df_daily = pd.DataFrame(df_daily)
        sar_daily = pd.DataFrame(sar_daily)
        macd_daily = pd.DataFrame(macd_daily)
        ema_daily8 = pd.DataFrame(ema_daily8)
        ema_daily21 = pd.DataFrame(ema_daily21)
        sma_daily = pd.DataFrame(sma_daily)
        rsi_daily = pd.DataFrame(rsi_daily)

        # Subseting dataframes to start at start_date and end at current_date
        sar_daily_short = sar_daily[start_date:dt_str]
        macd_daily_short = macd_daily[start_date:dt_str]
        ema_daily_short_first = ema_daily8[start_date:dt_str]
        ema_daily_short_second = ema_daily21[start_date:dt_str]
        sma_daily_short = sma_daily[start_date:dt_str]
        rsi_daily_short = rsi_daily[start_date:dt_str]

        # Individual Plot Elements:

        ## OHLC Candlestick Chart
        trace_candles = go.Candlestick(x=df_daily.index,  # df_daily.index stores dates (x-axis)
                                       open=df_daily.open,  # Open for OHLC candlesticks
                                       high=df_daily.high,  # High for OHLC candlesticks
                                       low=df_daily.low,  # Low for OHLC candlesticks
                                       close=df_daily.close,  # Close for OHLC candlesticks
                                       name='Candlestick')  # Naming this to Candlestick for legend on the side of plot

        ## OHLC Bar Chart
        trace_bars = go.Ohlc(x=df_daily.index,  # index stores dates (x-axis)
                             open=df_daily.open,  # Open for OHLC bars
                             high=df_daily.high,  # High for OHLC bars
                             low=df_daily.low,  # Low for OHLC bars
                             close=df_daily.close,  # Close for OHLC bars
                             name='Bar Chart')  # Naming this to Bar Chart

        ## Daily Close Line
        trace_close = go.Scatter(x=list(df_daily.index),  # index stores dates (x-axis)
                                 y=list(df_daily.close),  # want only close values plotted
                                 name='Close',  # Name this to Close
                                 line=dict(color='#87CEFA',  # Define color for line
                                           width=2))  # Define width for line

        # Open and Close markers
        d = 1  # Marker will be placed d position points above or below daily open/close valu, respectively.
        df_daily["marker"] = np.where(df_daily["open"] < df_daily["close"], df_daily["high"] + d, df_daily["low"] - d)
        df_daily["Symbol"] = np.where(df_daily["open"] < df_daily["close"], "triangle-up",
                                      "triangle-down")  # triangle up for + day, triangle down for - day
        df_daily["Color"] = np.where(df_daily["open"] < df_daily["close"], "green",
                                     "red")  # defining green positive change and red for negative daily change

        # Arrows corresponding to daily increasing/decreasing values
        trace_arrow = go.Scatter(x=list(df_daily.index),
                                 y=list(df_daily.marker),
                                 mode='markers',
                                 name='Markers',
                                 marker=go.scatter.Marker(size=8,
                                                          symbol=df_daily["Symbol"],
                                                          color=df_daily["Color"]))

        # 8 Day EMA over 21 Day EMA:

        ## EMA
        trace_ema8 = go.Scatter(x=list(ema_daily_short_first.index),
                                y=list(ema_daily_short_first.EMA),
                                name='8 Day EMA',
                                line=dict(color='#E45756',  # Define color for line
                                          width=1,  # Define width for line
                                          dash='dot'))  # Define dash (I want my line to be dotted)

        trace_ema21 = go.Scatter(x=list(ema_daily_short_second.index),
                                 y=list(ema_daily_short_second.EMA),
                                 name='21 Day EMA',
                                 line=dict(color='#4C78A8',  # Define color for line
                                           width=1,  # Define width for line
                                           dash='dot'))  # Define dash (I want my line to be dotted)

        ## SMA
        trace_sma = go.Scatter(x=list(sma_daily_short.index),
                               y=list(sma_daily_short.SMA),
                               name=str(sma_period) + ' Day SMA',
                               line=dict(color='#E45756',
                                         width=1,
                                         dash='dot'))

        ## Volume
        trace_volume = go.Bar(x=list(df_daily.index),
                              y=list(df_daily.volume),
                              name='Volume',
                              marker=dict(color='gray'),
                              yaxis='y2',
                              legendgroup='two')

        ## MACD Histogram
        trace_macd_hist = go.Bar(x=list(macd_daily_short.index),
                                 y=list(macd_daily_short.MACD_Hist),
                                 name='MACD Histogram',
                                 marker=dict(color='gray'),
                                 yaxis='y3',
                                 legendgroup='three')

        ## MACD Line
        trace_macd = go.Scatter(x=list(macd_daily_short.index),
                                y=list(macd_daily_short.MACD),
                                name='MACD',
                                line=dict(color='black', width=1.5),  # red
                                yaxis='y3',
                                legendgroup='three')

        ## MACD Signal Line
        trace_macd_signal = go.Scatter(x=list(macd_daily_short.index),
                                       y=list(macd_daily_short.MACD_Signal),
                                       name='Signal',
                                       line=dict(color='red', width=1.5),  # plum
                                       yaxis='y3',
                                       legendgroup='three')

        ## RSI
        trace_rsi = go.Scatter(x=list(rsi_daily_short.index),
                               y=list(rsi_daily_short.RSI),
                               mode='lines',
                               name='RSI',
                               line=dict(color='black',
                                         width=1.5),
                               yaxis='y4',
                               legendgroup='four')

        # RSI Overbought
        trace_rsi_70 = go.Scatter(mode='lines',
                                  x=[min(rsi_daily_short.index), max(rsi_daily_short.index)],
                                  y=[70, 70],
                                  name='Overbought > 70%',
                                  line=dict(color='green',
                                            width=0.5,
                                            dash='dot'),
                                  yaxis='y4',
                                  legendgroup='four')

        # RSI Oversold
        trace_rsi_30 = go.Scatter(mode='lines',
                                  x=[min(rsi_daily_short.index), max(rsi_daily_short.index)],
                                  y=[30, 30],
                                  name='Oversold < 30%',
                                  line=dict(color='red',
                                            width=0.5,
                                            dash='dot'),
                                  yaxis='y4',
                                  legendgroup='four')

        # RSI Center Line
        trace_rsi_50 = go.Scatter(mode='lines',
                                  x=[min(rsi_daily_short.index), max(rsi_daily_short.index)],
                                  y=[50, 50],
                                  line=dict(color='gray',
                                            width=0.5,
                                            dash='dashdot'),
                                  name='50%',
                                  yaxis='y4',
                                  legendgroup='four')

        ## Plotting Layout
        layout = go.Layout(xaxis=dict(titlefont=dict(color='rgb(200,115,115)'),  # Color of our X-axis Title
                                      tickfont=dict(color='rgb(100,100,100)'),  # Color of ticks on X-axis
                                      linewidth=1,  # Width of x-axis
                                      linecolor='black',  # Line color of x-axis
                                      gridwidth=1,  # gridwidth on x-axis marks
                                      gridcolor='rgb(204,204,204)',  # grid color
                                      # Define ranges to view data. I chose 3 months, 6 months, 1 year, and year to date
                                      rangeselector=dict(
                                          buttons=(dict(count=3, label='3 mo', step='month', stepmode='backward'),
                                                   dict(count=6, label='6 mo', step='month', stepmode='backward'),
                                                   dict(count=1, label='1 yr', step='year', stepmode='backward'),
                                                   dict(count=1, label='YTD', step='year', stepmode='todate'),
                                                   dict(step='all')))),
                           # Define different y-axes for each of our plots: daily, volume, MACD, and RSI -- hence 4 y-axes
                           yaxis=dict(domain=[0.40, 1.0], fixedrange=False,
                                      titlefont=dict(color='rgb(200,115,115)'),
                                      tickfont=dict(color='rgb(200,115,115)'),
                                      linecolor='black',
                                      mirror='all',
                                      gridwidth=1,
                                      gridcolor='rgb(204,204,204)'),
                           yaxis2=dict(domain=[0.26, 0.36], fixedrange=False, title='Volume',
                                       titlefont=dict(color='rgb(200,115,115)'),
                                       tickfont=dict(color='rgb(200,115,115)'),
                                       linecolor='black',
                                       mirror='all',
                                       gridwidth=1,
                                       gridcolor='rgb(204,204,204)'),
                           yaxis3=dict(domain=[0.13, 0.23], fixedrange=False, title='MACD',
                                       titlefont=dict(color='rgb(200,115,115)'),
                                       tickfont=dict(color='rgb(200,115,115)'),
                                       linecolor='black',
                                       constraintoward='center',  # might not be necessary
                                       mirror='all',
                                       gridwidth=1,
                                       gridcolor='rgb(204,204,204)'),
                           yaxis4=dict(domain=[0., 0.10], range=[10, 90], title='RSI',
                                       tick0=10, dtick=20,
                                       titlefont=dict(color='rgb(200,115,115)'),
                                       tickfont=dict(color='rgb(200,115,115)'),
                                       linecolor='black',
                                       mirror='all',
                                       gridwidth=1,
                                       gridcolor='rgb(204,204,204)'),
                           title=(ticker + ' Daily Data'),  # Give our plot a title
                           title_x=0.5,  # Center our title
                           paper_bgcolor='rgba(37,37,37,0)',  # Background color of main background
                           plot_bgcolor='rgb(226,238,245)',  # Background color of plot
                           height=900,  # overall height of plot
                           margin=dict(l=60, r=20, t=50, b=5)  # define margins: left, right, top, and bottom
                           )
        # All individual plots in data element
        plotting_data = [trace_close, trace_candles, trace_bars, trace_arrow, trace_ema8, trace_ema21, trace_sma,
                         trace_volume,
                         trace_macd_hist, trace_macd, trace_macd_signal, trace_rsi, trace_rsi_30, trace_rsi_50,
                         trace_rsi_70]

        # Plot
        fig = go.Figure(data=plotting_data, layout=layout)

        # Uncomment the following line to write your plot to full_figure.html, and auto open
        # fig.write_html('first_figure.html', auto_open=True)
        fig.show()

        # END OF full_plot #########################################

    def main(self):
        self.full_plot('AAPL')  # Change AAPL to any ticker of your choice that is supported by AlphaVantage


if __name__ == '__main__':
    plot = Plot()
    plot.main()
