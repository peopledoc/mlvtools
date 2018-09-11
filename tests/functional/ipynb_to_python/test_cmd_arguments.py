import tempfile
from os.path import join

import pytest

from tests.helpers.utils import gen_notebook
from mlvtools.exception import MlVToolException
from mlvtools.ipynb_to_python import IPynbToPython


def test_should_raise_if_missing_output_path_argument_and_no_conf():
    """
        Test command raise if output path is not provided when no conf
    """
    arguments = ['-n', './test.ipynb', '--working-directory', './']
    with pytest.raises(MlVToolException):
        IPynbToPython().run(*arguments)


def test_should_raise_if_output_path_exist_and_no_force():
    """
        Test command raise if output path already exists and no force argument
    """
    with tempfile.TemporaryDirectory() as work_dir:
        output_path = join(work_dir, 'py_script')
        with open(output_path, 'w') as fd:
            fd.write('')
        arguments = ['-n', './test.ipynb', '--working-directory', work_dir, '-o', output_path]
        with pytest.raises(MlVToolException):
            IPynbToPython().run(*arguments)


def test_should_overwrite_with_force_argument():
    """
        Test output paths are overwritten with force argument
    """
    with tempfile.TemporaryDirectory() as work_dir:
        notebook_path = gen_notebook(cells=['pass'], tmp_dir=work_dir, file_name='test_nb.ipynb')
        output_path = join(work_dir, 'py_script')
        with open(output_path, 'w') as fd:
            fd.write('')
        arguments = ['-n', notebook_path, '--working-directory', work_dir, '-o', output_path,
                     '--force']
        IPynbToPython().run(*arguments)
        with open(output_path, 'r') as fd:
            assert fd.read()
