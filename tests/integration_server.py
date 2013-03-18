"""Integration tests for the server

"""

import logging
import subprocess
import tempfile
import time
import unittest

import requests

class ServerIntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log = logging.getLogger("integration.server")
        cls.cache_folder = tempfile.mkdtemp("pypicache")
        # This assumes this port is free
        cmd = ["python", "-m", "pypicache.main", "--address", "127.0.0.1", "--port", "8484", cls.cache_folder]
        cls.log.info("Starting {0}".format(cmd))
        cls.server_process = subprocess.Popen(cmd)
        # TODO blech, need to know it's started
        time.sleep(5)
        assert cls.server_process.poll() is None

    @classmethod
    def tearDownClass(cls):
        cls.log.info("Shutting down process")
        cls.server_process.kill()
        cls.server_process.wait()

    def get(self, path, expected=200):
        uri = "http://127.0.0.1:8484{0}".format(path)
        self.log.debug("Fetching: {0}".format(uri))
        response = requests.get(uri)
        self.log.debug("Got response: {0}".format(response))
        self.assertEqual(response.status_code, expected)

    def test_index(self):
        self.get("/")

    def test_simple_index(self):
        self.get("/simple/")

    def test_simple_package(self):
        self.get("/simple/requests/")

if __name__ == '__main__':
    unittest.main()
