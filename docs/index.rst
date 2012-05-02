.. pypicache documentation master file, created by
   sphinx-quickstart on Wed May  2 22:43:11 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pypicache - A Proxying PyPI Cache
=================================

pypicache aims to solve some problems developers and teams encounter when using python packages:

1. Many python package installation tools will check all associated links for a python project on PyPI, which can be problematic when the project's server is down. Doubly so if the download link is on that server.

2. Commercial development of python projects might involve local patches to packages or completely private packages. It's useful to host these internally.

3. Hosting an internal proxy can save quite a bit of bandwidth, which might be an issue for some teams.

4. Installation of a larger project can be noticably faster from an internal server.

5. Continuous integration tools can potentially install large sets of packages again and again, which can consume upstream bandwidth and slow down builds.

pypicache can be used in the following ways:

1. As a straight proxy to PyPI, caching package downloads where possible.

2. As a completely standalone PyPI server, useful for deploying from.

3. As an internal server for hosting custom packages.

A possible day to day workflow could involve a pypicache server running on developer's machines or in an office. Developers would install packages via this server. This server can also be shared by a deployment build tool which would install from the completely local copy of packages. This allows for repeatable builds.

..
    Contents:

    .. toctree::
       :maxdepth: 2

    Indices and tables
    ==================

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`
