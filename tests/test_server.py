import unittest

import mock

from webtest import TestApp

from pypicache import cache
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

    def test_simple_package(self):
        self.mock_packagecache.pypi_get_simple_package_info.return_value = """<html><a href="mypackage">mypackage-1.0</a></html>"""
        response = self.app.get("/simple/mypackage/")
        self.assertIn("mypackage-1.0", response)
        self.mock_packagecache.pypi_get_simple_package_info.assert_called_with("mypackage")

    def test_local_package(self):
        self.mock_packagecache.local_get_simple_package_info.return_value = """<html><a href="mypackage">mypackage-1.0</a></html>"""
        response = self.app.get("/local/mypackage/")
        self.assertIn("mypackage-1.0", response)
        self.mock_packagecache.local_get_simple_package_info.assert_called_with("mypackage")

    def test_packages_source_sdist(self):
        self.mock_packagecache.get_sdist.return_value = "--package-data--"
        response = self.app.get("/packages/source/m/mypackage/mypackage-1.0.tar.gz")
        self.assertEqual("application/x-tar", response.headers["Content-Type"])
        self.assertEqual("--package-data--", response.body)
        self.mock_packagecache.get_sdist.assert_called_with("mypackage", "mypackage-1.0.tar.gz")

    def test_packages_source_notfound(self):
        def fail(*args, **kwargs):
            raise cache.NotFound("Unknown package")
        self.mock_packagecache.get_sdist.side_effect = fail
        self.app.get("/packages/source/m/mypackage/mypackage-1.1.tar.gz", status=404)
        self.mock_packagecache.get_sdist.assert_called_with("mypackage", "mypackage-1.1.tar.gz")
