"""Stores packages on disk

"""

import hashlib
import logging
import os

from pypicache import exceptions

class DiskPackageStore(object):
    def __init__(self, prefix):
        self.log = logging.getLogger("pypicache.disk")
        self.prefix = prefix

    def get_sdist_path(self, package, filename):
        firstletter = package[0]
        return os.path.join(self.prefix, "packages/source/{}/{}/{}".format(firstletter, package, filename))

    def list_sdists(self, package):
        firstletter = package[0]
        prefix = os.path.join(self.prefix, "packages/source/{}/{}".format(firstletter, package))
        self.log.debug("Using package prefix {!r}".format(prefix))
        for root, dirs, files in os.walk(prefix, topdown=False):
            self.log.info("Examining {} for sdists".format((root, dirs, files)))
            for filename in files:
                abspath = os.path.join(root, filename)
                yield dict(
                    package=package,
                    firstletter=firstletter,
                    sdist=filename,
                    md5=hashlib.md5(open(abspath).read()).hexdigest()
                )

    def list_packages(self):
        for root, dirs, files in os.walk(self.prefix):
            for packagename in dirs:
                yield packagename
            break

    def get_sdist(self, package, filename):
        path = self.get_sdist_path(package, filename)
        try:
            return open(path, "rb")
        except IOError:
            raise exceptions.NotFound("Package {}: {} not found in {}".format(package, filename, path))

    def add_sdist(self, package, filename, content):
        path = self.get_sdist_path(package, filename)
        if os.path.isfile(path):
            raise exceptions.NotOverwritingError("Not overwriting {}".format(path))
        prefix = os.path.dirname(path)
        if not os.path.isdir(prefix):
            self.log.debug("Making directories {}".format(prefix))
            os.makedirs(prefix)
        with open(path, "wb") as output:
            output.write(content)
