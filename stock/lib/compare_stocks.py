import matplotlib.pyplot as plt
import matplotlib.finance

def plot_compare_graph(df1, df2, name1, name2):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()
    matplotlib.finance.candlestick2_ochl(
        ax1, df1.open, df1.close, df1.high, df1.low, width=0.5, colorup="r", colordown="g", alpha=0.8)
    matplotlib.finance.candlestick2_ochl(
        ax2, df2.open, df2.close, df2.high, df2.low, width=0.5, colorup="b", colordown="k", alpha=0.2)
    ax1.set_xlabel('date')
    ax1.set_ylabel(name1)
    ax2.set_ylabel(name2)
    plt.show()

