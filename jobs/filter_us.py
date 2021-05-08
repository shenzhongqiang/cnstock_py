import os.path
import akshare as ak
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

df = ak.stock_us_fundamental()
df["eps_growth_5y"] = df["eps_growth_5y"].apply(lambda x: float(x) if x is not None else None)
df["market_val"] = df["market_val"].apply(lambda x: float(x))
df["pe_ratio_12m"] = df["pe_ratio_12m"].apply(lambda x: float(x))
df["peg_ratio"] = df["peg_ratio"].apply(lambda x: float(x))
df_res = df[df["eps_growth_5y"]>150][df["market_val"]>20000][df["pe_ratio_12m"]<20]

print(df_res.sort_values(["peg_ratio"]))
