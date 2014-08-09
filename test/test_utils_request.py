from stock.utils.request import *

class TestRequest:
    def test_send_request(self):
        resp = send_request('http://www.baidu.com')
        print resp
