import hashlib
import json
import logging
import os

try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib

import requests

SIMPLE_PACKAGE_PAGE_TEMPLATE = """
<html>
<head>
<title>Links for {package}</title>
</head>
<body>
<h1>Links for {package}</h1>

{links}

</body>
</html>
"""

SIMPLE_PACKAGE_PAGE_LINK_TEMPLATE = """<a href="/packages/source/{firstletter}/{package}/{sdist}#md5={md5}">{sdist}</a><br>"""

PYPI_PACKAGE_VERSION_JSON_LINK = "{server}pypi/{package}/{version}/json"

class PackageCacheError(Exception):
    """Base exception for PackageCache errors

    """

class RemoteError(PackageCacheError):
    """Raised when there is a problem talking to an upstream service

    """

class NotFound(PackageCacheError):
    """Raised when a given package or file isn't found

    Aims to encapsulate packages not present locally or remotely.

    """

class PackageCache(object):
    """A proxying cache for python packages

    Reads from PyPI and writes to a local location

    Tries to mirror the PyPI structure
    """
    def __init__(self, prefix, pypi_server="http://pypi.python.org/"):
        self.log = logging.getLogger("packagecache")

        # We always need a trailing slash for later templates
        if not pypi_server.endswith("/"):
            pypi_server = pypi_server + "/"
        self.pypi_server = pypi_server
        self.prefix = prefix
        # Certain operations aren't available via the JSON api (well, at least obviously)
        self.xmlrpc_client = xmlrpclib.ServerProxy("http://pypi.python.org/pypi")

    def pypi_get_versions(self, package):
        """Returns a list of available versions for a package

        This calls the PyPI XML-RPC API. See
        http://wiki.python.org/moin/PyPiXmlRpc

        :returns: A list of version strings

        """
        # TODO set the show_hidden to True, but very slow
        versions = self.xmlrpc_client.package_releases(package, False)
        self.log.debug("Got versions {} for package {!r}".format(versions, package))
        return versions

    def pypi_get_sdist_urls(self, package, version):
        """Get a list of URLS for the given package

        This takes the url info returned from the PyPI JSON API and only
        returns sdist urls dicts.

        See http://wiki.python.org/moin/PyPiJson

        """
        uri = PYPI_PACKAGE_VERSION_JSON_LINK.format(
            server=self.pypi_server,
            package=package,
            version=version,
        )
        self.log.info("Fetching JSON info from {}".format(uri))
        r = requests.get(uri)
        if r.status_code == 404:
            raise NotFound("Can't locate metadata for {}: {}".format(package, version))
        elif r.status_code != 200:
            raise RemoteError("Got {!r} from {!r}".format(r.status, uri))
        for url in json.loads(r.content)["urls"]:
            if url["packagetype"] == "sdist":
                yield url

    def pypi_get_simple_package_info(self, package):
        r = requests.get("{}simple/{}/".format(self.pypi_server, package))
        return r.content
        # TODO WIP in progress, trying to reproduce a simple page with links only
        # Better still to rewrite using local urls
        # self.log.info("Checking PyPI for links to {}".format(package))
        # links = []
        # for version in self.pypi_get_versions(package):
        #     self.log.debug("Found package {} version {}".format(package, version))
        #     for url in self.pypi_get_sdist_urls(package, version):
        #         self.log.debug("Found link {!r}".format(url))
        #         links.append("""<a href="{url}#md5={md5_digest}">{filename}</a>""".format(**url))

        # self.log.debug("Found links {}".format(links))
        # return SIMPLE_PACKAGE_PAGE_TEMPLATE.format(package=package, links="\n".join(links))

    def local_list_sdists(self, package):
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

    def local_get_simple_package_info(self, package):
        """Generate package info from local package information

        """
        links = []
        for sdist_info in self.local_list_sdists(package):
            links.append(SIMPLE_PACKAGE_PAGE_LINK_TEMPLATE.format(
                **sdist_info
            ))

        self.log.debug("Found links {}".format(links))
        return SIMPLE_PACKAGE_PAGE_TEMPLATE.format(package=package, links="\n".join(links))

    def get_sdist(self, package, filename):
        firstletter = package[0]
        path = "packages/source/{}/{}/{}".format(firstletter, package, filename)
        local_path = os.path.join(self.prefix, path)
        remote_path = os.path.join(self.pypi_server, path)
        try:
            self.log.debug("Trying local path {}".format(local_path))
            return open(local_path).read()
        except IOError:
            self.log.debug("Fetching from {}".format(remote_path))
            r = requests.get(remote_path)
            if r.status_code == 200:
                prefix = os.path.dirname(local_path)
                if not os.path.isdir(prefix):
                    self.log.debug("Making directories {}".format(prefix))
                    os.makedirs(prefix)
                with open(local_path, "wb") as fp:
                    fp.write(r.content)
                return open(local_path).read()
            else:
                raise NotFound("Can't locate a file for {}".format(path))

    def add_sdist(self, package, filename, file_fp):
        """Add a sdist tarball

        Won't overwrite.

        """
        # TODO merge common functionality with get_sdist above
        firstletter = package[0]
        path = "packages/source/{}/{}/{}".format(firstletter, package, filename)
        local_path = os.path.join(self.prefix, path)
        prefix = os.path.dirname(local_path)
        if not os.path.isdir(prefix):
            self.log.debug("Making directories {}".format(prefix))
            os.makedirs(prefix)
        if os.path.isfile(local_path):
            raise PackageCacheError("Can't overwrite existing package in {!r}".format(local_path))
        with open(local_path, "wb") as fp:
            self.log.info("Writing package {} sdist to {}".format(package, local_path))
            fp.write(file_fp.read())

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
            self.log.debug("Examining requirement {!r}".format(line))
            if "==" in line:
                package, version = line.split("==")
                try:
                    for url in self.pypi_get_sdist_urls(package, version):
                        self.log.debug("Looking at {!r}".format(url))
                        self.get_sdist(package, url["filename"])
                        processing_info["cached"].append(url["filename"])
                except NotFound:
                    processing_info["failed"].append(line)
            else:
                self.log.debug("Don't know how to handle {!r}".format(line))
                processing_info["unparseable"].append(line)
        return processing_info
