from stock.utils.symbol_util import *
import unittest
import os.path
import tushare as ts
import pandas as pd

class TestSymbolUtil(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_stock_symbol(self):
        symbols = get_stock_symbols()
        self.assertTrue(len(symbols) > 0)
        symbols = get_stock_symbols('sh')
        self.assertTrue(len(symbols) > 0)

    def test_get_index_symbols(self):
        indice = get_index_symbols()
        self.assertListEqual(indice, ['sz399001', 'sz399006', 'sh000001'])

    def test_get_index_symbol(self):
        index = get_index_symbol('sh')
        self.assertEqual(index, 'sh000001')

    def test_download_symbols(self):
        #download_symbols()
        self.assertTrue(os.path.isfile(SYM['all']))
        self.assertTrue(os.path.isfile(SYM['sh']))
        self.assertTrue(os.path.isfile(SYM['sz']))
        self.assertTrue(os.path.isfile(SYM['cy']))

    def test_get_trading_dates(self):
        dates = get_trading_dates()
        self.assertTrue(len(dates) > 0)

    def test_get_archived_trading_dates(self):
        dates = get_archived_trading_dates()
        self.assertTrue(len(dates) > 0)

    def test_is_symbol_cy(self):
        res = is_symbol_cy('sh600005')
        self.assertTrue(res == False)
        res = is_symbol_cy('sz300001')
        self.assertTrue(res == True)

    def test_is_symbol_sh(self):
        res = is_symbol_sh('sh600005')
        self.assertTrue(res == True)
        res = is_symbol_sh('sz000001')
        self.assertTrue(res == False)

    def test_is_symbol_sz(self):
        res = is_symbol_sz('sz000005')
        self.assertTrue(res == True)
        res = is_symbol_sz('sz300001')
        self.assertTrue(res == False)

    def test_is_symbol_kc(self):
        res = is_symbol_kc('kc688139')
        self.assertTrue(res == True)
        res = is_symbol_kc('sz300001')
        self.assertTrue(res == False)

    def test_is_st(self):
        res = is_st('sh603838')
        self.assertTrue(res == False)
        res = is_st('sz000927')
        self.assertTrue(res == True)

    def test_get_today_all(self):
        df = get_today_all()
        print(df)

    def test_get_realtime_by_date(self):
        df = get_realtime_by_date("2019-03-07")

    def test_get_realtime_date(self):
        date_str = get_realtime_date()
        print(date_str)

    def test_get_kaipan(self):
        s = get_kaipan("sz000983")
        print(s)

    def test_get_tick_by_date(self):
        df = get_tick_by_date("2019-04-01")
        print(df)

    def test_get_zhangting_data(self):
        date = '2019-04-24'
        df_tick = ts.get_tick_data('002547', date=date, src='tt')
        df_tick.loc[:, "time"] = pd.to_datetime(date + ' ' + df_tick["time"], format="%Y-%m-%d %H:%M:%S")
        high = df_tick.price.max()
        df_tick1 = df_tick[df_tick.time<=date + " 11:30:00"].copy()
        df_tick2 = df_tick[df_tick.time>=date + " 13:00:00"].copy()
        result = get_zhangting_data(df_tick2, high)
        print(result)

    def test_load_concept(self):
        df = load_concept()
        print(df)

    def test_load_industry(self):
        df = load_industry()
        print(df)
