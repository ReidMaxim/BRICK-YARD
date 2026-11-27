import unittest
from discovery.expand import merge,TOPICS
class ExpansionTests(unittest.TestCase):
    def test_preserve_existing(self):
        raw={"a/b":{"repo":"A/B","sources":["csv"],"level":0}}
        records={"a/b":{"repo":"A/B","description":"prior evidence"}}
        merge(raw,records,[{"full_name":"a/b","description":"new"}],"robotics")
        self.assertEqual(len(raw),1)
        self.assertEqual(records["a/b"]["description"],"prior evidence")
        self.assertEqual(raw["a/b"]["sources"],["csv","github-topic:robotics"])
    def test_new_metadata(self):
        raw={};records={}
        merge(raw,records,[{"full_name":"X/Y","license":{"spdx_id":"MIT"}}],"webgl")
        self.assertEqual(records["x/y"]["license"],"MIT")
        self.assertEqual(raw["x/y"]["level"],0)
    def test_topics(self):
        self.assertEqual(len(TOPICS),len(set(TOPICS)))
