import os
import json
import requests
import pandas as pd
from stock.globalvar import BASIC_DIR

def get_concepts():
    pz = 500
    i = 1
    result = []
    while True:
        url = "https://11.push2.eastmoney.com/api/qt/clist/get?pn={}&pz={}&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:90+t:3+f:!50&fields=f12,f14".format(i, pz)
        r = requests.get(url, verify=False)
        data = r.json()
        total = data["data"]["total"]
        items = data["data"]["diff"]
        result.extend(items)
        if (i-1)*pz+len(items) >= total:
            break
        i += 1
    result = list(map(lambda x: {"id": x["f12"], "name": x["f14"]}, result))
    return result

def get_industries():
    pz = 500
    i = 1
    result = []
    while True:
        url = "https://24.push2.eastmoney.com/api/qt/clist/get?pn={}&pz={}&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:90+t:2+f:!50&fields=f12,f14".format(i, pz)
        r = requests.get(url, verify=False)
        data = r.json()
        total = data["data"]["total"]
        items = data["data"]["diff"]
        result.extend(items)
        if (i-1)*pz+len(items) >= total:
            break
        i += 1
    result = list(map(lambda x: {"id": x["f12"], "name": x["f14"]}, result))
    return result

def get_concept_stocks(concept_id):
    pz = 500
    i = 1
    result = []
    while True:
        url = "https://push2.eastmoney.com/api/qt/clist/get?fid=f62&pn={}&po=1&pz={}&np=1&fltt=2&invt=2&fs=b%3A{}&fields=f12,f14".format(i, pz, concept_id)
        r = requests.get(url, verify=False)
        data = r.json()
        total = data["data"]["total"]
        items = data["data"]["diff"]
        result.extend(items)
        if (i-1)*pz+len(items) >= total:
            break
        i += 1
    result = list(map(lambda x: {"id": x["f12"], "name": x["f14"]}, result))
    return result

def get_industry_stocks(industry_id):
    pz = 500
    i = 1
    result = []
    while True:
        url = "https://push2.eastmoney.com/api/qt/clist/get?fid=f62&po={}&pz={}&pn=1&np=1&fltt=2&invt=2&fs=b%3A{}&fields=f12,f14".format(i, pz, industry_id)
        r = requests.get(url, verify=False)
        data = r.json()
        total = data["data"]["total"]
        items = data["data"]["diff"]
        result.extend(items)
        if (i-1)*pz+len(items) >= total:
            break
        i += 1
    result = list(map(lambda x: {"id": x["f12"], "name": x["f14"]}, result))
    return result

def get_all_concepts_stocks():
    concepts = get_concepts()
    s_concept = []
    s_symbol = []
    s_name = []
    for concept in concepts:
        concept_name = concept["name"]
        concept_id = concept["id"]
        stocks = get_concept_stocks(concept_id)
        symbols = list(map(lambda x: x["id"], stocks))
        names = list(map(lambda x: x["name"], stocks))
        s_concept.extend([concept_name]*len(stocks))
        s_symbol.extend(symbols)
        s_name.extend(names)
    df = pd.DataFrame({"concept": s_concept, "symbol": s_symbol, "name": s_name})
    filepath = os.path.join(BASIC_DIR, "concept")
    df.to_csv(filepath, index=False)

def get_all_industries_stocks():
    industries = get_industries()
    s_industry = []
    s_symbol = []
    s_name = []
    for industry in industries:
        industry_name = industry["name"]
        industry_id = industry["id"]
        stocks = get_industry_stocks(industry_id)
        symbols = list(map(lambda x: x["id"], stocks))
        names = list(map(lambda x: x["name"], stocks))
        s_concept.extend([industry_name]*len(stocks))
        s_symbol.extend(symbols)
        s_name.extend(names)
    df = pd.DataFrame({"industry": s_industry, "symbol": s_symbol, "name": s_name})
    filepath = os.path.join(BASIC_DIR, "industry")
    df.to_csv(filepath, index=False)

if __name__ == "__main__":
    get_all_concepts_stocks()
    get_all_industries_stocks()
