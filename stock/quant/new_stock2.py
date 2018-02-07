import demjson
import re
import pandas as pd
import seaborn as sns
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates
from stock.marketdata.storefactory import get_store
from stock.filter.utils import get_zt_price
import numpy as np
import requests
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix
from sklearn import linear_model
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from config import store_type
from stock.utils.symbol_util import symbol_to_exsymbol

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

def get_newstock(pages=10):
    url_patt = "http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=XGSG_LB&token=70f12f2f4f091e459a279469fe49eca5&st=purchasedate,securitycode&sr=-1&p=%d&ps=100&js=var%%20MeMNSnDm={pages:(tp),data:(x)}&rt=50599754"
    result = pd.DataFrame(columns=[
        "exsymbol",
        "subcode",
        "fxzl",
        "issueprice",
        "wsfxsl",
        "applyontMoney",
        "issuepriceMoney",
        "industrype",
        "peissuea",
    ])
    a_exsymbol = []
    a_subcode = []
    a_fxzl = []
    a_issueprice = []
    a_wsfxsl = []
    a_applyontMoney = []
    a_issuepriceMoney = []
    a_industrype = []
    a_peissuea = []
    for i in range(1, pages):
        url = url_patt % i
        r = requests.get(url)
        content = r.content
        matched = re.match(r"var \S+=({.*})", content)
        jsondata = matched.group(1)
        data = demjson.decode(jsondata)
        stocks = data["data"]
        for stock in stocks:
            symbol = stock["securitycode"]
            exsymbol = symbol_to_exsymbol(symbol)
            a_exsymbol.append(exsymbol)
            a_subcode.append(stock["subcode"])
            a_fxzl.append(stock["fxzl"])
            a_issueprice.append(stock["issueprice"])
            a_wsfxsl.append(stock["wsfxsl"])
            a_applyontMoney.append(stock["applyontMoney"])
            a_issuepriceMoney.append(stock["issuepriceMoney"])
            a_industrype.append(stock["INDUSTRYPE"])
            a_peissuea.append(stock["peissuea"])

    df = pd.DataFrame(data={
        "exsymbol": a_exsymbol,
        "subcode": a_subcode,
        "fxzl": a_fxzl,
        "issueprice": a_issueprice,
        "wsfxsl": a_wsfxsl,
        "applyontMoney": a_applyontMoney,
        "issuepriceMoney": a_issuepriceMoney,
        "industrype": a_industrype,
        "peissuea": a_peissuea
    })
    return df.iloc[50:]

def set_profit(df_stock):
    store = get_store(store_type)
    df_index = store.get('id000001')
    max_price = []
    for exsymbol in df_stock.index.values:
        df_history = store.get(exsymbol)
        high = df_history.high[:90].max()
        max_price.append(high)
    df_stock["max_price"] = max_price
    df_stock["guess"] = df_stock["industrype"] * df_stock["issueprice"]/df_stock["peissuea"]

def analyze(df_stock):
    df_test = df_stock.iloc[:500]
    df_test["result"] = df_test["max_price"] > df_test["guess"]*0.95
    print df_test[df_test.result == False][["max_price", "guess"]]
    print df_test.result.sum()*1.0/len(df_test)
    print df_test.corr()["max_price"]
    X = df_stock[["industrype", "issueprice"]]
    y = df_stock["max_price"]

    # linear model
    lr = linear_model.LinearRegression()
    lr.fit(X, y)
    ypred = lr.predict(X)
    print r2_score(y, ypred)

    # SVM model
    svm = SVR(kernel="linear")
    svm.fit(X, y)
    ypred = svm.predict(X)
    print r2_score(y, ypred)

    # RandomForest model
    rf = RandomForestRegressor(n_estimators=10)
    rf.fit(X, y)
    ypred = rf.predict(X)
    print r2_score(y, ypred)

    #scatter_matrix(df_stock, alpha=0.2, figsize=(20, 12))
    plt.scatter(df_stock["industrype"], df_stock["issueprice"], alpha=0.2, c=df_stock["max_price"], cmap="jet")
    plt.colorbar()
    plt.show()

if __name__ == "__main__":
    # get new stocks and save
    #df = get_newstock(12)
    #df = df[df.industrype != "-"]
    #df.to_csv("/tmp/newstock")

    # load new stocks from file
    df = pd.read_csv("/tmp/newstock", dtype={
        "applyontMoney": "f4",
        "exsymbol": "S10",
        "fxzl": "f4",
        "industrype": "f4",
        "issueprice": "f4",
        "issuepriceMoney": "f4",
        "peissuea": "f4",
        "subcode": "S10",
        "wsfxsl": "f4"
    })
    df.set_index("exsymbol", inplace=True)
    set_profit(df)
    analyze(df)
