import logging
import mimetypes
import re

from flask import (
    abort,
    Flask,
    jsonify,
    make_response,
    render_template,
    request,
)

from pypicache import exceptions

app = Flask("pypicache")

def configure_app(pypi, package_store, package_cache, debug=False, testing=False):
    app.debug = debug
    app.testing = testing
    app.config["pypi"] = pypi
    app.config["package_store"] = package_store
    app.config["cache"] = package_cache
    return app

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/simple/")
def simple_index():
    """The top level simple index page

    """
    return render_template("simple.html")

@app.route("/simple/<package>/")
def pypi_simple_package_info(package):
    return app.config["pypi"].get_simple_package_info(package)

@app.route("/local/<package>/")
def local_simple_package_info(package):
    sdists = list(app.config["package_store"].list_sdists(package))
    return render_template("simple_package.html",
        package=package,
        sdists=sdists,
    )

@app.route("/packages/source/<firstletter>/<package>/<filename>", methods=["GET"])
def get_sdist(firstletter, package, filename):
    try:
        response = make_response(app.config["cache"].get_sdist(package, filename))
        content_type, _ = mimetypes.guess_type(filename)
        logging.debug("Setting mime type of {!r} to {!r}".format(filename, content_type))
        response.content_type = content_type
        return response
    except exceptions.NotFound:
        return abort(404)

# @app.route("/packages/source/<firstletter>/<package>/<filename>", methods=["PUT"])
# def put_sdist(firstletter, package, filename):
#     """PUT a sdist package

#     """
#     # Flask doesn't appear to support a PUT request with raw content
#     # very well. Trying to figure out a magic combination to make it
#     # work.
#     print vars(request)
#     # fp = StringIO(list(request.form)[0])
#     assert request.data
#     fp = StringIO(request.data)
#     app.config["pypi"].add_sdist(package, filename, fp)
#     return jsonify({"uploaded": "ok"})

@app.route("/uploadpackage/", methods=["POST"])
def post_uploadpackage():
    """POST an sdist package

    """
    # TODO parse package versions properly, hopefully via distutils2 style library
    # Assume package in form <package>-<version>.tar.gz
    if "sdist" not in request.files:
        response = jsonify({"error": True, "message": "Missing sdist data."})
        response.status_code = 400
        return response
    filename = request.files["sdist"].filename
    package = re.match(r"(?P<package>.*?)-.*?\..*", filename).groupdict()["package"]
    logging.debug("Parsed {!r} out of {!r}".format(package, filename))
    app.config["package_store"].add_sdist(package, filename, request.files["sdist"].stream)
    return jsonify({"uploaded": "ok"})

@app.route("/requirements.txt", methods=["POST"])
def POST_requirements_txt():
    """POST a requirements.txt to get the packages therein

    """
    if "requirements" not in request.files:
        response = jsonify({"error": True, "message": "Missing requirements data."})
        response.status_code = 400
        return response
    return jsonify(app.config["cache"].cache_requirements_txt(request.files["requirements"].stream))
