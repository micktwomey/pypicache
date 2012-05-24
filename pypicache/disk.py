"""Stores packages on disk

"""

import hashlib
from glob import glob
import logging
import os

from pypicache import exceptions

class DiskPackageStore(object):
    def __init__(self, prefix):
        self.log = logging.getLogger("pypicache.disk")
        self.prefix = prefix

    def get_file_path(self, package, filename):
        firstletter = package[0]
        return os.path.join(self.prefix, "packages/{}/{}/{}".format(firstletter, package, filename))

    def list_files(self, package):
        firstletter = package[0]
        prefix = os.path.join(self.prefix, "packages/{}/{}".format(firstletter, package))
        self.log.debug("Using package prefix {!r}".format(prefix))
        for root, dirs, files in os.walk(prefix, topdown=False):
            self.log.info("Examining {} for files".format((root, dirs, files)))
            for filename in files:
                abspath = os.path.join(root, filename)
                yield dict(
                    package=package,
                    firstletter=firstletter,
                    filename=filename,
                    md5=hashlib.md5(open(abspath).read()).hexdigest()
                )

    def list_packages(self):
        path = os.path.join(self.prefix, "packages/source/?/*")
        self.log.info("Listing packages in {}".format(path))
        for packagename in sorted(glob(path)):
            if not os.path.isdir(packagename):
                continue
            yield os.path.basename(packagename)

    def get_file(self, package, filename):
        path = self.get_file_path(package, filename)
        try:
            return open(path, "rb")
        except IOError:
            raise exceptions.NotFound("Package {}: {} not found in {}".format(package, filename, path))

    def add_file(self, package, filename, content):
        path = self.get_file_path(package, filename)
        if os.path.isfile(path):
            raise exceptions.NotOverwritingError("Not overwriting {}".format(path))
        prefix = os.path.dirname(path)
        if not os.path.isdir(prefix):
            self.log.debug("Making directories {}".format(prefix))
            os.makedirs(prefix)
        with open(path, "wb") as output:
            output.write(content)
