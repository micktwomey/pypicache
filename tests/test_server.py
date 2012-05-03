import unittest

import mock

from webtest import TestApp

from pypicache import server

class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_packagecache = mock.Mock()
        self.app = TestApp(server.make_app(self.mock_packagecache))

    def test_index(self):
        response = self.app.get("/")
        self.assertIn("PyPI Cache", response.body)

    def test_static(self):
        self.app.get("/static/css/bootstrap.css")

    def test_simple(self):
        response = self.app.get("/simple")
        self.assertIn("simple", response.body)
