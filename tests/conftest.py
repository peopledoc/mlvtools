import tempfile

from pytest import fixture


@fixture
def work_dir():
    with tempfile.TemporaryDirectory() as work_dir:
        yield work_dir
