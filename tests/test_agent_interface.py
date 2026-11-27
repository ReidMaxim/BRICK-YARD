import unittest
from tools.warehouse import search,brief,load
class AgentInterfaceTests(unittest.TestCase):
    def test_rank(self):
        rows=[{"repo":"a/video","tags":["media"]},{"repo":"b/other","description":"video","tags":[]}]
        self.assertEqual(search(rows,"video")[0]["candidate"]["repo"],"a/video")
    def test_unknown(self):
        with self.assertRaises(ValueError): brief([],"a/b".split(),"goal")
    def test_real_inventory(self):
        rows=load();self.assertGreaterEqual(len(rows),222)
        self.assertTrue(search(rows,"animation"))
        out=brief(rows,[rows[0]["repo"]],"test")
        self.assertEqual(out["status"],"research hypothesis")
    def test_license(self):
        rows=[{"repo":"a/b","license":"MIT"},{"repo":"a/c","license":None}]
        self.assertEqual(len(search(rows,license_id="MIT")),1)
