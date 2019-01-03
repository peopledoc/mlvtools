from subprocess import SubprocessError

import pytest

from mlvtools.exception import MlVToolException
from mlvtools.helper import extract_type, to_dvc_meta_filename
from mlvtools.helper import to_cmd_param, to_method_name, to_bash_variable, to_script_name, get_git_top_dir, \
    to_dvc_cmd_name


def test_should_convert_to_command_param():
    """
        Test convert to command parameter
    """
    assert to_cmd_param('my_param_One') == 'my-param-One'


def test_should_convert_to_bash_variable():
    """
        Test convert to bash variable
    """
    assert to_bash_variable('my-param-one') == 'MY_PARAM_ONE'


def test_should_convert_to_method_name():
    """
        Test convert file name without extension to a python method name
    """
    assert to_method_name('01my-Meth$odk++ Name.truc') == 'mlvtools_01my_meth_odk_name_truc'


def test_should_convert_to_script_name():
    """
        Test convert file name to script name
    """
    assert to_script_name('My notebook.ipynb') == 'mlvtools_my_notebook.py'


def test_should_convert_to_dvc_meta_filename():
    """
        Test convert notebook path to dvc meta filename
    """
    assert to_dvc_meta_filename('./toto/truc/My notebook.ipynb') == 'my_notebook.dvc'


def test_should_extract_python_str_and_int():
    """
        Test extract python str and int types
    """
    type_info = extract_type('str ')
    assert type_info.type_name == 'str'
    assert not type_info.is_list
    type_info = extract_type(' int')
    assert type_info.type_name == 'int'
    assert not type_info.is_list


def test_should_return_none_if_extract_python_of_no_type():
    """
        Test extract python return None if empty type
    """
    type_info = extract_type('')
    assert not type_info.type_name
    assert not type_info.is_list
    type_info = extract_type(None)
    assert not type_info.type_name
    assert not type_info.is_list


def test_should_extract_python_list_type():
    """
        Test extract python list type
    """
    type_info = extract_type('list')
    assert type_info.type_name == 'str'
    assert type_info.is_list
    type_info = extract_type('List')
    assert type_info.type_name == 'str'
    assert type_info.is_list

    type_info = extract_type('list[str]')
    assert type_info.type_name == 'str'
    assert type_info.is_list
    type_info = extract_type('List[int]')
    assert type_info.type_name == 'int'
    assert type_info.is_list


def test_should_convert_to_dvc_cmd_name():
    """
        Test convert script name to dvc command name
    """
    assert to_dvc_cmd_name('my_notebook.py') == 'my_notebook_dvc'


def test_should_return_git_top_dir(work_dir, mocker):
    """
        Test get git top dir call subprocess
    """
    mocked_check_output = mocker.patch('subprocess.check_output', return_value=b'/work_dir')
    assert get_git_top_dir(work_dir) == '/work_dir'
    assert mocked_check_output.mock_calls == [mocker.call(
        ['git', 'rev-parse', '--show-toplevel'],
        cwd=work_dir)]


def test_should_raise_if_git_command_fail(work_dir, mocker):
    """
        Test a MlVTool message is raised if git command fail
    """
    mocker.patch('subprocess.check_output', side_effect=SubprocessError)
    with pytest.raises(MlVToolException) as e:
        get_git_top_dir(work_dir)
    assert isinstance(e.value.__cause__, SubprocessError)
