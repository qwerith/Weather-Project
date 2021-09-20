import unittest
from cache_check import *
from datetime import datetime
from unittest import mock
from unittest.mock import patch

class Cache_Check(unittest.TestCase):

    def test_input_type_check(self):
        self.assertEqual(input_type_check("123123"), "coords")
        self.assertEqual(input_type_check("ssdaasd"), "name")
    
    def test_upd_check(self):
        self.assertEqual(upd_check(datetime(2021, 9, 16, 15, 0)), None)
        self.assertEqual(upd_check(datetime.now()), True)
        self.assertRaises(Exception, upd_check, 1)
    
    def test_cache_check(self):
        with mock.patch("cache_check.input_type_check", return_value="name"):
            self.assertEqual(cache_check("123"), (None, "not_exists"))
        with mock.patch("cache_check.input_type_check", return_value="coords"):
            self.assertEqual(cache_check("lat=123&lon=45"), (None, "not_exists"))
    
    def test_check_by_id(self):
        self.assertEqual(check_by_id(-1), None)
        


