import unittest

from api.api import app


class MatchApiTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_options_returns_saved_filters(self):
        response = self.client.get("/api/options")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["tournaments"])
        self.assertTrue(response.json["seasons"])
        self.assertTrue(response.json["teams"])

    def test_matches_returns_json_with_pagination(self):
        response = self.client.get("/api/matches?tournament_id=1&limit=2")

        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json)
        self.assertIn("pagination", response.json)
        self.assertLessEqual(len(response.json["data"]), 2)

    def test_matches_rejects_invalid_played_filter(self):
        response = self.client.get("/api/matches?played=2")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
