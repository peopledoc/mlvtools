
.PHONY: help develop clean test release

#: help - Display callable targets.
help:
	@echo "Reference card for usual actions in development environment."
	@echo "Here are available targets:"
	@egrep -o "^#: (.+)" [Mm]akefile  | sed 's/#: /* /'


#: develop - Install minimal development utilities.
develop:
	pip install -e .[dev]

#: clean - Basic cleanup, mostly temporary files.
clean:
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '__pycache__' -delete
	rm -rf *.egg
	rm -rf *.egg-info
	rm -rf ./build
	rm -rf ./package
	rm -rf ./dist

#: test - Run test suites.
test:
	pytest ./tests

#: lint - Run lint test.
lint:
	flake8 ./mlvtools ./tests ./cmd

package:
	python setup.py sdist bdist_wheel -d ./package

test-pypi-upload:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

pypi-upload:
	twine upload dist/*