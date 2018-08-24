
.PHONY: help develop clean test release

#: help - Display callable targets.
help:
	@echo "Reference card for usual actions in development environment."
	@echo "Here are available targets:"
	@egrep -o "^#: (.+)" [Mm]akefile  | sed 's/#: /* /'


#: develop - Install minimal development utilities.
develop:
	pip install -e .

#: clean - Basic cleanup, mostly temporary files.
clean:
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	rm -rf *.egg
	rm -rf *.egg-info

#: test - Run test suites.
test:
	pytest ./mlvtool/tests

#: lint - Run lint test.
lint:
	flake8 ./mlvtool

release:
	pip install zest.releaser
	fullrelease
