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
        sorted_plan = Uniform.parse_fenhong_output(file)
        self.assertTrue(len(sorted_plan) > 0)
        file = os.path.join(HIST_DIR['fenhong'], 'sh600005')
        sorted_plan = Uniform.parse_fenhong_output(file)
        self.assertTrue(len(sorted_plan) > 0)
