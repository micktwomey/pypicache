.PHONY: help init pip-review test integration-test coverage runserver docs push dist

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
	pip install -r requirements.txt -r dev-requirements.txt --use-mirrors

pip-review: init
	pip-review

pip-dump: init
	pip-dump

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
	git push origin master
	git push github master

dist:
	python setup.py sdist
