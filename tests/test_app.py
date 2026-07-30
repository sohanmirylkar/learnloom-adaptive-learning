import unittest

from app import create_app
from nlp import analyze_feedback


class LearnLoomTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test", "MONGODB_URI": None})
        self.client = self.app.test_client()

    def test_register_dashboard_and_feedback(self):
        response = self.client.post("/register", data={
            "name": "Ada Learner", "email": "ada@example.com",
            "password": "safe-password", "interests": ["python", "nlp"],
        }, follow_redirects=True)
        self.assertIn(b"Good to see you, Ada", response.data)
        response = self.client.post("/feedback", data={"feedback": "The lesson was clear and helpful"}, follow_redirects=True)
        self.assertIn(b"positive", response.data)

    def test_nlp_signal(self):
        self.assertEqual(analyze_feedback("I am stuck; this is confusing")["sentiment"], "negative")

    def test_health(self):
        self.assertEqual(self.client.get("/health").status_code, 200)


if __name__ == "__main__":
    unittest.main()

