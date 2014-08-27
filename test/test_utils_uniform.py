from stock.utils.uniform import *
import unittest
import os.path
from stock.globalvar import *

class TestUtilsUniform(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_fenhong_output(self):
        file = os.path.join(HIST_DIR['fenhong'], 'sz300059')
        parse_fenhong_output(file)
