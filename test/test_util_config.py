import unittest, sys, os

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mock"))

from bb_change_broker.util.config import parse_filters


class TestConfig(unittest.TestCase):
    def test_parse_filters(self):
        filters = "root,trunk,-php,1,2|root,branches,device,1,5|root,branches,version,1,4|root,branches,Win32Software,1,5|root,branches,1,3|root,tags,1,4|MDB_Daten,trunk,0,3"
        exp_filters = [
            (["root", "trunk", "-php"], 1, 2),
            (["root", "branches", "device"], 1, 5),
            (["root", "branches", "version"], 1, 4),
            (["root", "branches", "Win32Software"], 1, 5),
            (["root", "branches"], 1, 3),
            (["root", "tags"], 1, 4),
            (["MDB_Daten", "trunk"], 0, 3),
        ]
        self.assertEqual(parse_filters(filters), exp_filters)

    def test_parse_filters2(self):
        filters = "root,trunk,-php,1,2|project,branches,0,3"
        exp_filters = [
            (["root", "trunk", "-php"], 1, 2),
            (["project", "branches"], 0, 3),
        ]
        self.assertEqual(parse_filters(filters), exp_filters)
