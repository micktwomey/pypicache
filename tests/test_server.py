import unittest

from webtest import TestApp

from pypicache import server

class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = TestApp(server.app)

    def test_index(self):
        response = self.app.get("/")
        self.assertIn("PyPI Cache", response.body)

    def test_simple(self):
        response = self.app.get("/simple")
        self.assertIn("simple", response.body)
