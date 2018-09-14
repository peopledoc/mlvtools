from os.path import join

import pytest

from mlvtools.exception import MlVToolException
from mlvtools.script_to_cmd import MlScriptToCmd
from tests.helpers.utils import write_min_script


def test_should_raise_if_missing_py_command_output_path_argument_and_no_conf():
    """
        Test command raise if python command output path is not provided when no conf
    """
    arguments = ['-i', './test.py', '--working-directory', './', '--out-dvc-cmd', './out_cmd']
    with pytest.raises(MlVToolException):
        MlScriptToCmd().run(*arguments)


def test_should_raise_if_missing_dvc_command_output_path_argument_and_no_conf():
    """
        Test command raise if dvc command output path is not provided when no conf
    """
    arguments = ['-i', './test.py', '--working-directory', './', '--out-py-cmd', './out_py_cmd']
    with pytest.raises(MlVToolException):
        MlScriptToCmd().run(*arguments)


def test_should_raise_if_py_command_output_path_exist_and_no_force(work_dir):
    """
        Test command raise if python output path already exists and no force argument
    """
    py_cmd_output = join(work_dir, 'py_out')
    with open(py_cmd_output, 'w') as fd:
        fd.write('')
    arguments = ['-i', './test.py', '--working-directory', work_dir, '--out-dvc-cmd', './out_dvc_cmd',
                 '--out-py-cmd', py_cmd_output]
    with pytest.raises(MlVToolException):
        MlScriptToCmd().run(*arguments)


def test_should_raise_if_dvc_command_output_path_exist_and_no_force(work_dir):
    """
        Test command raise if dvc output path already exists and no force argument
    """
    dvc_cmd_output = join(work_dir, 'dvc_out')
    with open(dvc_cmd_output, 'w') as fd:
        fd.write('')
    arguments = ['-i', './test.py', '--working-directory', work_dir, '--out-py-cmd', './out_py_cmd',
                 '--out-dvc-cmd', dvc_cmd_output]
    with pytest.raises(MlVToolException):
        MlScriptToCmd().run(*arguments)


def test_should_overwrite_with_force_argument(work_dir):
    """
        Test output paths are overwritten with force argument
    """
    script_path = join(work_dir, 'script_path.py')
    write_min_script(script_path)

    py_cmd_path = join(work_dir, 'py_cmd')
    dvc_cmd_path = join(work_dir, 'dvc_cmd')
    for path in (py_cmd_path, dvc_cmd_path):
        with open(path, 'w') as fd:
            fd.write('')

    arguments = ['-i', script_path, '--out-py-cmd', py_cmd_path, '--out-dvc-cmd', dvc_cmd_path,
                 '--working-directory', work_dir, '--force']
    MlScriptToCmd().run(*arguments)

    with open(py_cmd_path, 'r') as fd:
        assert fd.read()
    with open(dvc_cmd_path, 'r') as fd:
        assert fd.read()
