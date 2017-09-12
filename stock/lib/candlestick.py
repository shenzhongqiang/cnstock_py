import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates

def plot_compare_graph(df_index, df_stock, name_index, name_stock, show_marker=False):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()
    ax1.plot(df_index.index, df_index.close, c='b')
    ax2.plot(df_stock.index, df_stock.close, c='r')
    ax1.set_xlabel('date')
    ax1.set_ylabel(name_index)
    ax2.set_ylabel(name_stock)

    if show_marker:
        df_index["chg"] = df_index.close.pct_change()
        df_stock["chg"] = df_stock.close.pct_change()
        idxs = df_stock[df_index.chg < -0.01][df_stock.chg > 0].index
        for idx in idxs:
            ax1.axvline(x=idx, linewidth=1, c='k')
    fig.autofmt_xdate()
    plt.show()

def plot_candlestick(df, name):
    xdate = pd.to_datetime(df.index)
    def mydate(x, pos):
        try:
            return xdate[x]
        except IndexError:
            return ''

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(df.index, df.close, c='b')
    ax1.set_ylabel(name)
    fig.autofmt_xdate()
    plt.show()

def plot_price_volume_inday(times, prices, volumes):
    fig = plt.figure()
    fmt = matplotlib.dates.DateFormatter("%H:%M:%S")
    x = np.arange(len(times))
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()
    ax1.plot(x, prices, c='b')
    ax2.plot(x, volumes, c='k', alpha=0.2)
    #ax1.xaxis.set_major_formatter(fmt)
    ax1.set_xlim(x[0], x[len(x)-1])
    ax2.set_ylim(0)
    ax1.set_xlabel('time')
    ax1.set_ylabel('close')
    ax2.set_ylabel('volume')
    plt.show()
