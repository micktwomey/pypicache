.PHONY: test all

help:
	@echo "Commands:"
	@echo "1. make test - run unittests"
	@echo "2. python -m pypicache.main - run the server (prints help)"

test:
	python -m unittest discover
