import unittest

import mock

from pypicache import cache
from pypicache import disk
from pypicache import pypi

class CacheTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_pypi = mock.Mock(spec=pypi.PyPI)
        self.mock_packages = mock.Mock(spec=disk.DiskPackageStore)
        self.cache = cache.PackageCache(self.mock_packages, self.mock_pypi)

    # @unittest.skip("TODO")
    # def test_get_sdist(self):
    #     raise NotImplementedError()

    # @unittest.skip("TODO")
    # def test_cache_requirements_txt(self):
    #     raise NotImplementedError()
