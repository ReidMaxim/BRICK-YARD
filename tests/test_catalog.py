import json, unittest, tempfile
from pathlib import Path
from discovery.collect import normalize, import_csv
ROOT=Path(__file__).resolve().parents[1]
class CatalogTests(unittest.TestCase):
    def test_seed(self):
        rows=json.loads((ROOT/"docs/catalog.json").read_text())
        self.assertGreaterEqual(len(rows),15)
        self.assertEqual(len(rows),len({x["id"] for x in rows}))
        self.assertEqual(len(rows),len({x["repo"].lower() for x in rows}))
        for x in rows:
            self.assertEqual(normalize(x["repo"]),x["repo"])
            self.assertIn(x["level"],range(4))
            for key in ("input","output","license","source","compatibility","evidence","runtime"):
                self.assertIn(key,x)
    def test_normalize(self):
        self.assertEqual(normalize("https://github.com/a/b.git"),"a/b")
        for bad in ("https://evil.example/a/b","a/b/c","a/..","a/b?x=y"):
            with self.assertRaises(ValueError): normalize(bad)
    def test_csv(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"data.csv";p.write_text("url\nhttps://github.com/a/b\nhttps://github.com/a/b\ninvalid\n")
            self.assertEqual(import_csv(p),["a/b"])
