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

class NotOverwritingError(PackageCacheError):
    """Raised when attempting to overwrite an existing file

    """
