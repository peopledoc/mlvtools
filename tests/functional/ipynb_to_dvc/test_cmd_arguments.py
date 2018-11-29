import glob
from os.path import join, exists, basename

import pytest
from pytest import fixture

from mlvtools.conf.conf import DEFAULT_CONF_FILENAME
from mlvtools.exception import MlVToolException
from mlvtools.helper import to_script_name, to_dvc_cmd_name
from mlvtools.ipynb_to_dvc import IPynbToDvc
from tests.helpers.utils import gen_notebook, write_conf


@fixture
def input_notebook(work_dir):
    return gen_notebook(cells=['pass'], tmp_dir=work_dir, file_name='test_nb.ipynb')


@fixture
def script_name(input_notebook):
    return to_script_name(basename(input_notebook))


@fixture
def dvc_name(script_name):
    return to_dvc_cmd_name(script_name)


def write_test_conf(work_dir: str, conf_path: str = None):
    dvc_dir = join(work_dir, 'dvc')
    script_dir = join(work_dir, 'scritps')
    conf_path = conf_path if conf_path else join(work_dir, DEFAULT_CONF_FILENAME)
    write_conf(work_dir=work_dir, conf_path=conf_path,
               script_dir=script_dir, dvc_cmd_dir=dvc_dir)
    return script_dir, dvc_dir


def test_should_raise_if_no_conf(input_notebook):
    """
        Test command raise if no conf, neither auto detected or given to command line
    """
    arguments = ['-n', input_notebook, '--working-directory', './']
    with pytest.raises(MlVToolException):
        IPynbToDvc().run(*arguments)


def test_should_take_auto_detected_conf(work_dir, input_notebook, script_name, dvc_name):
    """
        Test command run with auto detected conf
    """
    script_dir, dvc_dir = write_test_conf(work_dir)
    arguments = ['-n', input_notebook, '--working-directory', work_dir]
    IPynbToDvc().run(*arguments)
    assert exists(script_dir)
    assert len(glob.glob(join(script_dir, script_name))) == 1
    assert exists(dvc_dir)
    assert len(glob.glob(join(dvc_dir, dvc_name))) == 1


def test_should_conf_from_param(work_dir, input_notebook, script_name, dvc_name):
    """
        Test command run with conf from command line arguments
    """
    conf_path = join(work_dir, 'a_conf.yml')
    script_dir, dvc_dir = write_test_conf(work_dir, conf_path)
    arguments = ['-n', input_notebook, '--working-directory', work_dir, '--conf', conf_path]
    IPynbToDvc().run(*arguments)
    assert exists(script_dir)
    assert len(glob.glob(join(script_dir, script_name))) == 1
    assert exists(dvc_dir)
    assert len(glob.glob(join(dvc_dir, dvc_name))) == 1


@pytest.mark.parametrize('output', ('script', 'dvc'))
def test_should_raise_if_output_file_exists_and_no_force(work_dir, input_notebook, output, script_name, dvc_name):
    """
        Test should raise if output exists and no force option
    """
    script_dir, dvc_dir = write_test_conf(work_dir)
    out = join(script_dir, script_name) if output == 'script' else join(dvc_dir, dvc_name)
    with open(out, 'w') as fd:
        fd.write('')
    arguments = ['-n', input_notebook, '--working-directory', work_dir]
    with pytest.raises(MlVToolException):
        IPynbToDvc().run(*arguments)


@pytest.mark.parametrize('output', ('script', 'dvc'))
def test_should_overwrite_with_force_argument(work_dir, input_notebook, script_name, dvc_name, output):
    """
        Test output paths are overwritten with force argument
    """
    script_dir, dvc_dir = write_test_conf(work_dir)
    out = join(script_dir, script_name) if output == 'script' else join(dvc_dir, dvc_name)
    with open(out, 'w') as fd:
        fd.write('')
    arguments = ['-n', input_notebook, '--working-directory', work_dir, '--force']
    IPynbToDvc().run(*arguments)
    with open(out, 'r') as fd:
        assert fd.read()
