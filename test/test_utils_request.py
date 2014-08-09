from stock.utils.request import *
import os

class TestRequest:
    def setup(self):
        self.request = Request()

    def test_send_request(self):
        resp = self.request.send_request('http://data.gtimg.cn/flashdata/hushen/latest/daily/sh000001.js?maxage=43201')
        assert len(resp) > 0

    def test_download_file(self):
        self.request.download_file('http://data.gtimg.cn/flashdata/hushen/latest/daily/sh000001.js?maxage=43201', '/tmp/sh000001')
        assert os.path.isfile('/tmp/sh000001')
        os.remove('/tmp/sh000001')
