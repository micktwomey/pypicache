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
	PYTHONPATH=. py.test --verbose --tb=short

coverage:
	PYTHONPATH=. coverage run -m py.test --verbose --tb=short
	coverage report --include 'pypicache*'
	coverage html --include 'pypicache*' -d build/coverage

docs:
	cd docs ; make html

runserver:
	PYTHONPATH=. python -m pypicache.main --debug --reload /tmp/pypicache

push:
	git push origin
	git push github master
