import os
import re
from lxml import etree
from selenium import webdriver
import requests
import pandas as pd
from stock.utils.symbol_util import symbol_to_exsymbol
from stock.globalvar import BASIC_DIR


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
}

def get_cookie(concept_id):
    url = "http://q.10jqka.com.cn/gn/detail/code/{}".format(concept_id)
    webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    mydriver = webdriver.PhantomJS()
    mydriver.set_window_size(1120, 550)
    mydriver.get(url)
    cookie = mydriver.get_cookies()[0]
    return {cookie["name"]: cookie["value"]}

def get_page_stocks(concept_id, page_id):
    url = "http://q.10jqka.com.cn/gn/detail/field/264648/order/desc/page/{}/ajax/1/code/{}".format(page_id, concept_id)
    print(concept_id, page_id)
    cookie = get_cookie(concept_id)
    r = requests.get(url, headers=headers, timeout=30, cookies=cookie)
    content = r.content
    root = etree.HTML(content)
    stock_nodes = root.xpath('.//tbody/tr/td[2]/a')
    if len(stock_nodes) == 0:
        print("error with cookie")
    exsymbols = []
    for node in stock_nodes:
        symbol = node.text
        print(concept_id, symbol)
        exsymbol = symbol_to_exsymbol(symbol)
        exsymbols.append(exsymbol)
    return exsymbols

def get_concept_stocks(url):
    r = requests.get(url, headers=headers, timeout=30)
    content = r.content
    matched = re.search(r'http://q.10jqka.com.cn/gn/detail/code/(\d+)', url)
    if not matched:
        raise Exception("error with url. not concept code")
    concept_id = matched.group(1)
    root = etree.HTML(content)
    pi_nodes = root.xpath('.//span[@class="page_info"]')
    page_num = 1
    if len(pi_nodes) > 0:
        pi_text = pi_nodes[0].text
        matched = re.match(r'1/(\d+)', pi_text)
        if not matched:
            raise Exception("cannot get page num")
        page_num = int(matched.group(1))

    exsymbols = []
    for i in range(1, page_num+1, 1):
        some_exsymbols = get_page_stocks(concept_id, i)
        exsymbols.extend(some_exsymbols)
    return exsymbols

def save_concepts():
    url = "http://q.10jqka.com.cn/gn/"
    r = requests.get(url, headers=headers, timeout=30)
    content = r.content
    root = etree.HTML(content)
    cate_nodes = root.xpath('.//div[@class="cate_items"]/a')
    s_concept = []
    s_exsymbol = []
    for node in cate_nodes:
        concept_name = node.text
        concept_url = node.attrib["href"]
        exsymbols = get_concept_stocks(concept_url)
        s_concept.extend([concept_name]*len(exsymbols))
        s_exsymbol.extend(exsymbols)
    df = pd.DataFrame({"concept": s_concept, "exsymbol": s_exsymbol})
    filepath = os.path.join(BASIC_DIR, "concept")
    df.to_csv(filepath)


if __name__ == "__main__":
    save_concepts()
