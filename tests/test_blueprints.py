import json,unittest
from pathlib import Path
class BlueprintTests(unittest.TestCase):
    def test_inventory_grounding(self):
        root=Path(__file__).resolve().parents[1]/"docs"
        rows=json.loads((root/"warehouse.json").read_text())
        inventory={x["repo"].lower() for x in rows}
        ideas=json.loads((root/"blueprints.json").read_text())
        self.assertEqual(len(ideas),10)
        self.assertEqual(len({x["id"] for x in ideas}),10)
        for idea in ideas:
            self.assertEqual(idea["status"],"hypothesis")
            self.assertGreaterEqual(len(set(idea["bricks"])),2)
            self.assertTrue(all(r.lower() in inventory for r in idea["bricks"]),idea["id"])
            self.assertTrue(idea["first_mission"])
