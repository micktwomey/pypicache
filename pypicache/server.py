import logging
import mimetypes
import os
import re

import bottle

from pypicache import cache

app = bottle.Bottle()

def make_app(package_cache):
    app.config["pypi"] = package_cache
    # Not 100% sure this is the best way to handle this.
    bottle.TEMPLATE_PATH.append(os.path.join(os.path.dirname(__file__), "templates"))
    return app

@app.route("/")
@bottle.jinja2_view("index")
def index():
    return {}

@app.route('/static/<path:path>')
def callback(path):
    root = os.path.join(os.path.dirname(__file__), "static")
    return bottle.static_file(path, root=root)

@app.route("/simple")
@app.route("/simple/")
@bottle.jinja2_view("simple")
def simple_index():
    """The top level simple index page

    """
    return {}

@app.route("/simple/<package>")
@app.route("/simple/<package>/")
def pypi_simple_package_info(package):
    return app.config["pypi"].pypi_get_simple_package_info(package)

@app.route("/local/<package>")
@app.route("/local/<package>/")
def local_simple_package_info(package):
    return app.config["pypi"].local_get_simple_package_info(package)

@app.route("/packages/source/<firstletter>/<package>/<filename>", "GET")
def get_sdist(firstletter, package, filename):
    try:
        content_type, _ = mimetypes.guess_type(filename)
        logging.debug("Setting mime type of {!r} to {!r}".format(filename, content_type))
        bottle.response.content_type = content_type
        return app.config["pypi"].get_sdist(package, filename)
    except cache.NotFound:
        return bottle.NotFound()

@app.route("/packages/source/<firstletter>/<package>/<filename>", "PUT")
def put_sdist(firstletter, package, filename):
    """

    Upload using:

    curl -X PUT --data-binary @dist/mypackage-1.0.tar.gz http://localhost:8080/packages/source/m/mypackage/mypackage-1.0.tar.gz

    """
    app.config["pypi"].add_sdist(package, filename, bottle.request.body)
    return {"uploaded": "ok"}

@app.route("/uploadpackage/<filename>", "POST")
def post_sdist(filename):
    """

    POST using:

    curl -X POST --data-binary @dist/mypackage-1.0.tar.gz http://localhost:8080/uploadpackage/mypackage-1.0.tar.gz

    """
    # TODO parse package versions properly, hopefully via distutils2 style library
    # Assume package in form <package>-<version>.tar.gz
    package = re.match(r"(?P<package>.*?)-.*?\..*", filename).groupdict()["package"]
    logging.debug("Parsed {!r} out of {!r}".format(package, filename))
    return app.config["pypi"].add_sdist(package, filename, bottle.request.body)

@app.route("/requirements.txt", "POST")
def POST_requirements_txt():
    """POST a requirements.txt to get the packages therein

    Works best with:

    pip freeze | curl  -X POST --data-binary @- http://localhost:8080/requirements.txt | python -m json.tool

    or

    curl -X POST --data-binary @/tmp/requirements.txt http://localhost:8080/requirements.txt | python -m json.tool

    """
    return app.config["pypi"].cache_requirements_txt(bottle.request.body)
