from stock.utils import request
import os

class TestRequest:
    def setup(self):
        pass

    def test_send_request(self):
        resp = request.send_request('http://data.gtimg.cn/flashdata/hushen/latest/daily/sh000001.js?maxage=43201')
        assert len(resp) > 0

    def test_download_file(self):
        request.download_file('http://data.gtimg.cn/flashdata/hushen/latest/daily/sh000001.js?maxage=43201', '/tmp/sh000001')
        assert os.path.isfile('/tmp/sh000001')
        os.remove('/tmp/sh000001')
