import unittest

import logging
import mock

from webtest import TestApp

from pypicache import cache
from pypicache import disk
from pypicache import exceptions
from pypicache import pypi
from pypicache import server

class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_packagecache = mock.Mock(spec=cache.PackageCache)
        self.mock_packagestore = mock.Mock(spec=disk.DiskPackageStore)
        self.mock_pypi = mock.Mock(spec=pypi.PyPI)
        self.app = TestApp(server.configure_app(self.mock_pypi, self.mock_packagestore, self.mock_packagecache, testing=True))

    def test_index(self):
        response = self.app.get("/")
        self.assertIn(b"PyPI Cache", response.body)

    def test_static(self):
        self.app.get("/static/css/bootstrap.css")

    def test_simple(self):
        response = self.app.get("/simple")
        self.assertIn(b"simple", response.body)

    def test_simple_package(self):
        content = """<html><a href="mypackage">mypackage-1.0</a></html>"""
        self.mock_pypi.get_simple_package_info.return_value = content
        response = self.app.get("/simple/mypackage/")
        self.assertEqual(response.body, content)

    def test_local_package(self):
        self.mock_packagestore.list_files.return_value = [dict(
            package="mypackage",
            firstletter="m",
            filename="mypackage-1.0.tar.gz",
            md5="ahashabcdef"
        )]
        response = self.app.get("/local/mypackage/")
        self.assertIn("""<a href="/packages/mypackage/mypackage-1.0.tar.gz#md5=ahashabcdef">mypackage-1.0.tar.gz</a>""", response.body)
        self.mock_packagestore.list_files.assert_called_with("mypackage")

    def test_packages_source_sdist(self):
        for url in [
            "/packages/source/M/MyPackage/MyPackage-1.0.tar.gz",
            "/packages/MyPackage/MyPackage-1.0.tar.gz",
        ]:
            logging.info("Testing url {0}".format(url))
            self.mock_packagecache.get_file.return_value = "--package-data--"
            response = self.app.get(url)
            self.assertEqual("application/x-tar", response.headers["Content-Type"])
            self.assertEqual(b"--package-data--", response.body)

            self.mock_packagecache.get_file.assert_called_with("MyPackage", "MyPackage-1.0.tar.gz", python_version=None)

    def test_packages_source_notfound(self):
        def fail(*args, **kwargs):
            raise exceptions.NotFound("Unknown package")
        self.mock_packagecache.get_file.side_effect = fail
        self.app.get("/packages/source/m/mypackage/mypackage-1.1.tar.gz", status=404)
        self.mock_packagecache.get_file.assert_called_with("mypackage", "mypackage-1.1.tar.gz", python_version=None)

    @unittest.skip("Need to figure out PUT under flask")
    def test_put_package_file(self):
        response = self.app.put("/packages/source/m/mypackage/mypackage-1.0.tar.gz", "--package-data--")
        self.assertDictEqual(response.json, {"uploaded": "ok"})
        self.assertTrue(self.mock_packagecache.add_file.called)
        args, kwargs = self.mock_packagecache.add_file.call_args
        self.assertEqual(args[:2], ("mypackage", "mypackage-1.0.tar.gz"))
        self.assertEqual(args[2].getvalue(), b"--package-data--")

    def test_post_packge_file(self):
        response = self.app.post("/uploadpackage/",
            upload_files=[("package", "mypackage-1.0.tar.gz", b"--package-data--")]
        )
        self.assertDictEqual(response.json, {"uploaded": "ok"})
        self.assertTrue(self.mock_packagestore.add_file.called)
        args, kwargs = self.mock_packagestore.add_file.call_args
        self.assertEqual(args[:2], ("mypackage", "mypackage-1.0.tar.gz"))
        self.assertEqual(args[2].getvalue(), b"--package-data--")

    def test_post_missing_package_data(self):
        """Test a post with no pacakge data

        """
        response = self.app.post("/uploadpackage/", status=400)
        self.assertDictEqual(response.json, {"error": True, "message": "Missing package data."})

    def test_post_requirements_txt(self):
        self.mock_packagecache.cache_requirements_txt.return_value = {"processed": "requirements"}
        response = self.app.post("/requirements.txt",
            upload_files=[("requirements", "requirements.txt", b"mypackage==1.0")]
        )
        self.assertDictEqual(response.json, {"processed": "requirements"})
        args, kwargs = self.mock_packagecache.cache_requirements_txt.call_args
        self.assertEqual(args[0].getvalue(), b"mypackage==1.0")

    def test_post_no_requirements_txt(self):
        """Test a post to requirements.txt without a upload_files

        """
        response = self.app.post("/requirements.txt", status=400)
        self.assertDictEqual(response.json, {"error": True, "message": "Missing requirements data."})

    def test_packages_bdist(self):
        self.mock_packagecache.get_file.return_value = "--package-data--"
        response = self.app.get("/packages/2.7/m/mypackage/mypackage-1.0-py2.7.egg")
        self.assertEqual("application/zip", response.headers["Content-Type"])
        self.assertEqual(b"--package-data--", response.body)

        self.mock_packagecache.get_file.assert_called_with("mypackage", "mypackage-1.0-py2.7.egg", python_version="2.7")
