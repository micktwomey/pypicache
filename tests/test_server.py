import unittest

import mock

from webtest import TestApp

from pypicache import cache
from pypicache import server

class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_packagecache = mock.Mock(spec=cache.PackageCache)
        self.app = TestApp(server.make_app(self.mock_packagecache, ))

    def test_index(self):
        response = self.app.get("/")
        self.assertIn(b"PyPI Cache", response.body)

    def test_static(self):
        self.app.get("/static/css/bootstrap.css")

    def test_simple(self):
        response = self.app.get("/simple")
        self.assertIn(b"simple", response.body)

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
        self.assertEqual(b"--package-data--", response.body)

        self.mock_packagecache.get_sdist.assert_called_with("mypackage", "mypackage-1.0.tar.gz")

    def test_packages_source_notfound(self):
        def fail(*args, **kwargs):
            raise cache.NotFound("Unknown package")
        self.mock_packagecache.get_sdist.side_effect = fail
        self.app.get("/packages/source/m/mypackage/mypackage-1.1.tar.gz", status=404)
        self.mock_packagecache.get_sdist.assert_called_with("mypackage", "mypackage-1.1.tar.gz")

    def test_put_packages_source_sdist(self):
        response = self.app.put("/packages/source/m/mypackage/mypackage-1.0.tar.gz", "--package-data--")
        self.assertDictEqual(response.json, {"uploaded": "ok"})
        self.assertTrue(self.mock_packagecache.add_sdist.called)
        args, kwargs = self.mock_packagecache.add_sdist.call_args
        self.assertEqual(args[:2], ("mypackage", "mypackage-1.0.tar.gz"))
        self.assertEqual(args[2].getvalue(), "--package-data--")

    def test_post_sdist(self):
        response = self.app.post("/uploadpackage/",
            upload_files=[("sdist", "mypackage-1.0.tar.gz", "--package-data--")]
        )
        self.assertDictEqual(response.json, {"uploaded": "ok"})
        self.assertTrue(self.mock_packagecache.add_sdist.called)
        args, kwargs = self.mock_packagecache.add_sdist.call_args
        self.assertEqual(args[:2], ("mypackage", "mypackage-1.0.tar.gz"))
        self.assertEqual(args[2].getvalue(), "--package-data--")

    def test_post_requirements_txt(self):
        self.mock_packagecache.cache_requirements_txt.return_value = {"processed": "requirements"}
        response = self.app.post("/requirements.txt",
            upload_files=[("requirements", "requirements.txt", "mypackage==1.0")]
        )
        self.assertDictEqual(response.json, {"processed": "requirements"})
        args, kwargs = self.mock_packagecache.cache_requirements_txt.call_args
        self.assertEqual(args[0].getvalue(), "mypackage==1.0")
