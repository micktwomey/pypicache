.PHONY: help init test integration-test coverage runserver docs push dist

help:
	@echo "make commands:"
	@echo "  make init - setup dependencies (pip install)"
	@echo "  make test - run unittests"
	@echo "  make integration-test - run a local server and integration tests"
	@echo "  make coverage - run tests and generate coverage report"
	@echo "  make docs - build HTML docs"
	@echo "  make runserver - runs a local server"
	@echo "  make push - git push to origins"

# If only we had a package cache :)
init:
	pip install -r requirements-develop.txt --use-mirrors

# This is really weird, py.test adds bin/ to the pythonpath which causes
# python 3 to fail, as bottle.py (the command line tool) isn't python 3
# compatible (mind you, it'd fail anyway if it was importing a script).
# Can work around this by using python -m instead. Or not use bottle
test:
	PYTHONPATH=. python -m py.test --verbose -l

integration-test:
	PYTHONPATH=. python -m py.test --verbose -l tests/integration_*.py

coverage:
	PYTHONPATH=. coverage run -m py.test
	coverage report --include 'pypicache*'
	coverage html --include 'pypicache*' -d build/coverage

docs:
	cd docs ; make html

runserver:
	PYTHONPATH=. python -m pypicache.main --debug --reload /tmp/pypicache

push:
	git push origin
	git push github master

dist:
	python setup.py sdist
