Large tests
===========

Those tests are high level tests, they are executed on a mlvtools packaged version.

The `./large_tests.sh` script creates the **mlvtools** wheel,
it installs it and then it runs all tests from `tests/large`.


Run in CI
---------

The [CircleCI](https://circleci.com/gh/peopledoc/mlvtools/) step **large-tests** runs
the `./large_tests.sh` script in the **python:3.6** Docker image.


Run locally
-----------

Large tests can be run locally using a new virtual environment or the provided docker image.

Use *large-test-local* Makefile step to run a container in which the `./large_tests.sh` script is executed.

The local Docker run is based on the **python:3.6** image. Your user is used inside the container
so created files in volumes will be yours.

