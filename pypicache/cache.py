import logging

from pypicache import exceptions

class PackageCache(object):
    """A proxying cache for python packages

    Reads from PyPI and writes to a local location

    Tries to mirror the PyPI structure
    """
    def __init__(self, package_store, pypi):
        self.log = logging.getLogger("packagecache")
        self.pypi = pypi
        self.package_store = package_store

    def get_file(self, package, filename, python_version=None):
        """Fetches a package file

        Attempts to use the local cache before falling back to PyPI.

        :returns: package file data

        - TODO: Change to returning a iterable

        """
        def get():
            return self.package_store.get_file(package, filename).read()
        try:
            return get()
        except exceptions.NotFound:
            # TODO change to iterating over a http response
            content = self.pypi.get_file(package, filename, python_version=python_version)
            self.package_store.add_file(package, filename, content)
            return get()

    def cache_requirements_txt(self, requirements_fp):
        """Take a requirements.txt file and cache packages

        This will parse a given requirements file, looking for packages
        to cache. This will only handle definitive versions, not
        relative ones.

        :parm requirements_fp: File object containing a requirements.txt

        """
        processing_info = {
            "cached": [],
            "unparseable": [],
            "failed": [],
        }
        for line in (line.strip() for line in requirements_fp):
            self.log.debug("Examining requirement {0!r}".format(line))
            if "==" in line:
                package, version = line.split("==")
                try:
                    for url in (url for url in self.pypi.get_urls(package, version) if url["packagetype"] == "sdist"):
                        self.log.debug("Looking at {0!r}".format(url))
                        self.get_file(package, url["filename"])
                        processing_info["cached"].append(url["filename"])
                except exceptions.NotFound:
                    processing_info["failed"].append(line)
            else:
                self.log.debug("Don't know how to handle {0!r}".format(line))
                processing_info["unparseable"].append(line)
        return processing_info
