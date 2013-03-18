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

@app.route("/local/")
def local_index():
    """Top level of local packages

    """
    return render_template("local_index.html",
        packages=list(app.config["package_store"].list_packages()),
    )

@app.route("/local/<package>/")
def local_simple_package_info(package):
    files = list(app.config["package_store"].list_files(package))
    return render_template("simple_package.html",
        package=package,
        files=files,
    )

@app.route("/packages/<package>/<filename>", methods=["GET"])
@app.route("/packages/<python_version>/<firstletter>/<package>/<filename>", methods=["GET"])
@app.route("/packages/source/<firstletter>/<package>/<filename>", methods=["GET"])
def get_file(package, filename, python_version=None, firstletter=None):
    logging.debug("Request to get package with: {0} {1} {2} {3}".format(firstletter, package, filename, python_version))
    try:
        response = make_response(app.config["cache"].get_file(package, filename, python_version=python_version))
        content_type, _ = mimetypes.guess_type(filename)
        if content_type is None and filename.endswith(".egg"):
            content_type = "application/zip"
        logging.debug("Setting mime type of {0!r} to {1!r}".format(filename, content_type))
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
    """POST a package

    """
    # TODO parse package versions properly, hopefully via distutils2 style library
    # Assume package in form <package>-<version>.tar.gz
    if "package" not in request.files:
        response = jsonify({"error": True, "message": "Missing package data."})
        response.status_code = 400
        return response
    filename = request.files["package"].filename
    package = re.match(r"(?P<package>.*?)-.*?\..*", filename).groupdict()["package"]
    logging.debug("Parsed {0!r} out of {1!r}".format(package, filename))
    app.config["package_store"].add_file(package, filename, request.files["package"].stream)
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
