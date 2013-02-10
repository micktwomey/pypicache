"""Amazon based pypi hosting

"""

from cStringIO import StringIO
import collections
import logging
import os.path

import boto

from pypicache import exceptions

class AmazonPackageStore(object):
    def __init__(self, bucketname, aws_key=None, aws_secret_key=None):
        self.log = logging.getLogger("pypicache.amazon")
        self.connection = boto.connect_s3(aws_access_key_id=aws_key, aws_secret_access_key=aws_secret_key)
        self.bucket = self.connection.get_bucket(bucketname)
        self.bucket.set_acl("public-read")

    def _list_all_files(self):
        """Yields all the packages and filenames

        :yields: tuples of (package, filename, boto.s3.key)

        """
        for key in self.bucket.list():
            path, filename = os.path.split(key.key)  # yields (path, filename)
            if filename:
                yield (os.path.basename(path), filename, key)

    def _get_public_url(self, key):
        """Generate a publich url for the given key

        Currently this assumes the resources have been made public.

        """
        url = key.generate_url(60 * 60 * 24 * 365, force_http=True)
        url = url.split("?")[0]  # pull it apart and assume public
        return url

    def list_files(self, package):
        for key in self.bucket.list(prefix="packages/{}/{}/".format(package[0], package)):
            path, filename = os.path.split(key.key)  # yields (path, filename)
            if filename:
                yield dict(
                    package=package,
                    firstletter=package[0],
                    filename=filename,
                    md5=key.md5,
                    url=self._get_public_url(key),
                )

    def list_packages(self):
        packages = set()
        for package, filename, key in self._list_all_files():
            packages.add(package)
        return sorted(packages)

    def get_file(self, package, filename):
        key = self.bucket.get_key("/packages/{}/{}/{}".format(package[0], package, filename))
        if key is not None:
            return StringIO(key.get_contents_as_string())
        raise exceptions.NotFound("Package {}: {} not found".format(package, filename))

    def add_file(self, package, filename, content):
        key = self.bucket.new_key("/packages/{}/{}/{}".format(package[0], package, filename))
        key.set_contents_from_string(content, policy="public-read", reduced_redundancy=True)

    def regenerate_indexes(self):
        """Regenerates static indexes in the S3 bucket

        This allows for use without this server, just with plain HTTP
        publishing.

        This is currently a little hack I have to unstick a problem with
        local hosting.

        """
        flat_index = ["<html><body>"]
        top_index = ["<html><body>"]
        per_package_index = collections.defaultdict(lambda: ["<html><body>"])
        for package, filename, key in self._list_all_files():
            if filename and package.strip() and not filename.endswith(".html"):
                flat_index.append("""<p><a href="{}">{}</a></p>""".format(self._get_public_url(key), filename))
                per_package_index[package].append("""<p><a href="{}">{}</a></p>""".format(self._get_public_url(key), filename))

        html_content_type ={"Content-Type": "text/html"}
        flat_html = "\n".join(flat_index + ["</body></html"])
        self.log.debug("flat.html:\n{}".format(flat_html))
        self.bucket.new_key("flat.html").set_contents_from_string(flat_html, policy="public-read", reduced_redundancy=True, headers=html_content_type)

        for package, files in sorted(per_package_index.iteritems()):
            top_index.append("""<p><a href="packages/{}/{}">{}</a></p>""".format(package[0], package, package))
            package_html = "\n".join(files + ["</body></html"])
            for filename in [
                "packages/{}/{}/index.html".format(package[0], package),
                "{}/index.html".format(package),
            ]:
                self.log.debug("{}:\n{}".format(filename, package_html))
                self.bucket.new_key(filename).set_contents_from_string(package_html, policy="public-read", reduced_redundancy=True, headers=html_content_type)

        index_html = "\n".join(top_index + ["</body></html"])
        self.log.debug("index.html:\n{}".format(index_html))
        self.bucket.new_key("index.html").set_contents_from_string(index_html, policy="public-read", reduced_redundancy=True, headers=html_content_type)

    def sort_files(self):
        """Hack to sort out misnamed packages

        If you've been using a disk based package store on osx then
        you'll encounter mixed case issues.

        This walks the S3 repository and copies keys to their correct
        name, and then removes the old key.

        """
        for package, filename, key in self._list_all_files():
            if filename.endswith("html"):
                continue
            # print package, filename, key, key.key
            expected_key = "packages/{}/{}/{}".format(package[0], package, filename)
            if expected_key != key.key:
                self.log.info("Copying {!r} to {!r}".format(key.key, expected_key))
                key.copy(self.bucket, expected_key, reduced_redundancy=True, preserve_acl=True)
                new_key = self.bucket.get_key(expected_key)
                self.log.info("Got new key {!r}".format(new_key))
                assert new_key is not None
                self.log.info("Deleting old key {!r}".format(key))
                key.delete()
