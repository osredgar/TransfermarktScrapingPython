import unittest

from api.api import app


class MatchApiTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_options_returns_saved_filters(self):
        response = self.client.get("/api/options")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["tournaments"])
        self.assertEqual(response.json["seasons"], [])

        response = self.client.get("/api/options?tournament_id=1")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["seasons"])

    def test_matches_returns_json_with_pagination(self):
        response = self.client.get("/api/matches?tournament_id=1&season=2026&limit=2")

        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json)
        self.assertIn("pagination", response.json)
        self.assertLessEqual(len(response.json["data"]), 2)
        self.assertTrue(all("events" in match for match in response.json["data"]))
        self.assertTrue(all(isinstance(match["events"], list) for match in response.json["data"]))
        self.assertTrue(all(list(match)[-1] == "events" for match in response.json["data"]))

    def test_matches_rejects_invalid_played_filter(self):
        response = self.client.get("/api/matches?played=2")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
