import numpy as np
import pandas as pd

def get_pulse_in_range(df, idx):
    num = 100
    if idx < num:
        return [np.nan, np.nan]
    df_train = df.iloc[idx-num: idx]
    diffs = (df_train.price - df_train.shift(1).price).tolist()[1:]
    min_indice = []
    max_ranges = []
    for i in range(len(diffs)):
        if i == 0:
            max_ranges.append(diffs[i])
            min_indice.append(i)
            continue

        if max_ranges[-1]+diffs[i] > diffs[i]:
            max_ranges.append(max_ranges[-1]+diffs[i])
            min_indice.append(min_indice[-1])
        else:
            max_ranges.append(diffs[i])
            min_indice.append(i)

    idx = np.argmax(max_ranges)
    end_idx = idx + 1
    start_idx = min_indice[idx]
    pulse_range = df_train.iloc[end_idx].price - df_train.iloc[start_idx].price
    pulse_vol = df_train.iloc[start_idx:end_idx+1].volume.sum()
    return [pulse_range, pulse_vol]

def get_pulse_info(df):
    close = df.iloc[-1].price
    vol_sum = df.volume.sum()
    for i in range(len(df)):
        idx = df.index[i]
        [pulse, pulse_vol] = get_pulse_in_range(df, i)
        df.loc[idx, "pulse"] = pulse / close
        df.loc[idx, "pulse_vol"] = pulse_vol * 1.0 / vol_sum

    pulse_idx = df.sort_values(["pulse"]).dropna().index[-1]
    pulse_row = df.loc[pulse_idx]
    return [pulse_row.pulse, pulse_row.pulse_vol]
