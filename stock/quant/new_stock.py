import pandas as pd
import seaborn as sns
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates
from stock.marketdata.storefactory import get_store
from stock.filter.utils import get_zt_price
import matplotlib.pyplot as plt
from config import store_type

def get_zt_num(df):
    num = 0
    for i in range(1, len(df.index)):
        row_yest = df.ix[i-1]
        row_today = df.ix[i]
        zt_price = get_zt_price(row_yest.close)

        if abs(zt_price - row_today.close) < 1e-2:
            num += 1
        else:
            break
    return num

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_index = store.get('id000001')
dates_len = len(df_index.date)
start_date = df_index.index[0]
columns = ['exsymbol', 'ipo_date', 'ipo_open', 'high', 'zt_num', 'zt_close', 'up_ratio']
df = pd.DataFrame(columns=columns)
for exsymbol in exsymbols:
    all_history = store.get(exsymbol)
    hist_len = len(all_history.date)
    hist_start_date = all_history.index[0]
    hist_start_open = all_history.ix[0].open
    #if hist_len < dates_len and \
    #    hist_start_date > start_date and \
    #    hist_start_open > 20 and hist_start_open <=30:
    if hist_len < dates_len and hist_start_date > start_date:
        high = all_history.high[:30].max()
        zt_num = get_zt_num(all_history)
        df.loc[len(df)] = [exsymbol, hist_start_date, hist_start_open, high, zt_num, all_history.close[zt_num], high/hist_start_open]

print df.zt_num.quantile(0.75)
print df.zt_num.quantile(0.5)
print df.zt_num.quantile(0.25)
print df.up_ratio.quantile(0.75)
print df.up_ratio.quantile(0.5)
print df.up_ratio.quantile(0.25)
sns.lmplot(x='ipo_open', y='up_ratio', data=df, fit_reg=False)
plt.show()
