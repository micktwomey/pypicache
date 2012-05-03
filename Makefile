.PHONY: help init test coverage runserver docs push

help:
	@echo "make commands:"
	@echo "  make init - setup dependencies (pip install)"
	@echo "  make test - run unittests"
	@echo "  make coverage - run tests and generate coverage report"
	@echo "  make docs - build HTML docs"
	@echo "  make runserver - runs a local server"
	@echo "  make push - git push to origins"

init:
	pip install -r requirements-develop.txt --use-mirrors

test:
	PYTHONPATH=. python -m unittest discover -s tests

coverage:
	PYTHONPATH=. coverage run -m unittest discover -s tests
	coverage report --include 'pypicache*'
	coverage html --include 'pypicache*' -d build/coverage

docs:
	cd docs ; make html

runserver:
	PYTHONPATH=. python -m pypicache.main /tmp/pypicache

push:
	git push origin
	git push github master
