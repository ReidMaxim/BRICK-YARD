import unittest
from discovery.sort_station import build
class SortingTests(unittest.TestCase):
    def test_canonical_duplicates(self):
        rows=build([{"repo":"A/B"}],[{"repo":"a/b","license":"MIT"},{"repo":"A/B","license":"MIT"}],[])
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["level"],0)
        self.assertEqual(rows[0]["license_group"],"permissive candidate")
    def test_seed_preserved(self):
        rows=build([{"repo":"a/b"}],[],[{"repo":"A/B","category":"games","name":"Seed","level":0}])
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["stage"],"seed")
    def test_raw_not_promoted(self):
        self.assertEqual(build([{"repo":"a/b"}],[],[])[0]["stage"],"discovered")
