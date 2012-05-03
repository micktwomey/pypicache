.PHONY: help test runserver docs

help:
	@echo "make commands:"
	@echo "  make test - run unittests"
	@echo "  make docs - build HTML docs"
	@echo "  make runserver - runs a local server"

test:
	PYTHONPATH=. python -m unittest discover -s tests

coverage:
	PYTHONPATH=. coverage run -m unittest discover -s tests
	coverage report --include 'pypicache*'
	coverage html --include 'pypicache*' -d build/coverage

runserver:
	PYTHONPATH=. python -m pypicache.main /tmp/pypicache

docs:
	cd docs ; make html
