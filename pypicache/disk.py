"""Stores packages on disk

"""

import hashlib
from glob import glob
import logging
import os

from pypicache import exceptions

def format_url(package, firstletter, filename, md5):
    return "/packages/{package}/{filename}#md5={md5}".format(package=package, filename=filename, md5=md5)

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
        # Try fishing for correct name
        if not os.path.isdir(prefix):
            self.log.info("Fishing for package matching {}".format(package))
            g = None
            for my_package in self.list_packages():
                if my_package.lower() == package.lower():
                    g = self.list_files(my_package)
                    break
            if g is not None:
                for i in g:
                    yield i
                return
        for root, dirs, files in os.walk(prefix, topdown=False):
            self.log.info("Examining {} for files".format((root, dirs, files)))
            for filename in files:
                abspath = os.path.join(root, filename)
                info = dict(
                    package=package,
                    firstletter=firstletter,
                    filename=filename,
                    md5=hashlib.md5(open(abspath).read()).hexdigest(),
                )
                info["url"] = format_url(**info)
                yield info

    def list_packages(self):
        path = os.path.join(self.prefix, "packages/?/*")
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
            self.log.info("Fishing for package file matching {}: {}".format(package, filename))
            # Try fishing for the file with different cases
            for my_package in self.list_packages():
                if package.lower() == my_package.lower():
                    for fileinfo in self.list_files(my_package):
                        my_filename = fileinfo["filename"]
                        if my_filename.lower() == filename.lower():
                            return self.get_file(my_package, my_filename)
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
            # TODO this is working around a difference in file obj vs string somewhere
            if hasattr(content, "read"):
                content = content.read()
            output.write(content)
