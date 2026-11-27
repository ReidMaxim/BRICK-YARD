import unittest
from discovery.signals import csv_repos,rss_repos,merge,extract
from discovery.rank import classify
class SignalsTests(unittest.TestCase):
    def test_csv_url(self):
        rows,cols=csv_repos("github_url,description\nhttps://github.com/Owner/Repo,ignore me\n")
        self.assertEqual(rows,{"Owner/Repo"})
    def test_csv_split(self):
        self.assertEqual(csv_repos("owner,repo\na,b\n")[0],{"a/b"})
    def test_rss(self):
        self.assertEqual(rss_repos("<rss><channel><item><title>a/b</title></item></channel></rss>"),{"a/b"})
    def test_merge(self):
        rows=merge([],{"csv":{"A/B"},"rss":{"a/b"}})
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["sources"],["csv","rss"])
    def test_invalid(self):
        self.assertIsNone(extract("https://evil.example/a/b"))
        self.assertIsNone(extract("https://github.com/topics/game"))
    def test_rank(self):
        self.assertIn("games",classify({"repo":"a/terrain","license":"MIT"})["tags"])
