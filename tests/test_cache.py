import unittest

import mock

from pypicache import cache

class CacheTestCase(unittest.TestCase):

    @mock.patch("pypicache.cache.xmlrpclib")
    def test_pypi_get_versions(self, mock_xmlrpclib):
        mock_proxy = mock.Mock()
        mock_xmlrpclib.ServerProxy.return_value = mock_proxy
        mock_proxy.package_releases.return_value = ["1.2", "1.3"]
        c = cache.PackageCache(mock.sentinel.prefix)
        self.assertListEqual(c.pypi_get_versions("fakepackage"), ["1.2", "1.3"])
        mock_xmlrpclib.ServerProxy.assert_called_with("http://pypi.python.org/pypi")
        mock_proxy.package_releases.assert_called_with("fakepackage", False)
