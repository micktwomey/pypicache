import argparse
import logging

from pypicache import cache
from pypicache import server

def main():
    parser = argparse.ArgumentParser(
        description="A PYPI cache",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("prefix", help="Package prefix, e.g. /tmp/packages")
    parser.add_argument("--address", default="0.0.0.0", help="Address to bind to")
    parser.add_argument("--port", default=8080, help="Port to listent on")
    parser.add_argument("--debug", default=False, action="store_true", help="Turn on debugging?")
    parser.add_argument("--reload", default=False, action="store_true", help="Turn on automatic reloading on code changes")
    parser.add_argument("--processes", default=1, type=int, help="Number of processes to run")
    args = parser.parse_args()

    loglevel = logging.DEBUG if args.debug else logging.INFO

    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s [%(levelname)s] [%(processName)s-%(threadName)s] [%(name)s] [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S%z"
    )
    logging.info("Debugging: {!r}".format(args.debug))
    logging.info("Reloading: {!r}".format(args.reload))

    package_cache = cache.PackageCache(args.prefix)
    app = server.configure_app(package_cache, debug=args.debug)
    app.run(host=args.address, port=args.port, debug=args.debug, use_reloader=args.reload, processes=args.processes)

if __name__ == '__main__':
    main()
