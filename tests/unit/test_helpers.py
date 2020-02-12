import stat
from os import stat as os_stat
from os.path import join, exists
from tempfile import TemporaryDirectory

import pytest
from jinja2 import UndefinedError, TemplateSyntaxError

from mlvtools.exception import MlVToolException
from mlvtools.helper import extract_type, to_dvc_meta_filename, to_instructions_list, \
    write_python_script, write_template, to_sanitized_path
from mlvtools.helper import to_cmd_param, to_method_name, to_bash_variable, to_script_name, to_dvc_cmd_name


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


def test_should_convert_to_instructions_list():
    """
        Test convert a string of several instructions into a list of instructions
    """
    assert to_instructions_list('\nimport os\na = 45\n') == ['import os', 'a = 45']


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


def test_should_sanitize_path():
    """
        Test should add ./ to path if does not start wiht / or ./
    """
    assert to_sanitized_path('toto.py') == './toto.py'


def test_sanitize_should_not_change_absolute_path():
    """
        Test sanitize should not change absolute path
    """
    absolute_path = '/absolut/path/toto.py'
    assert to_sanitized_path(absolute_path) == absolute_path


def test_sanitize_should_not_change_path_starting_with_dot_slash():
    """
        Test sanitize should not change path starting with dot slash
    """
    path = './toto.py'
    assert to_sanitized_path(path) == path


@pytest.fixture
def valid_template_path(work_dir):
    template_data = 'a_value={{ given_data }}'
    template_path = join(work_dir, 'template.tpl')
    with open(template_path, 'w') as fd:
        fd.write(template_data)
    return template_path


def test_should_write_template(work_dir, valid_template_path):
    """
        Test write an executable file from a given template and data
    """
    output_path = join(work_dir, 'my_exe.sh')
    write_template(output_path, valid_template_path, given_data='test')

    assert exists(output_path)
    assert stat.S_IMODE(os_stat(output_path).st_mode) == 0o755

    with open(output_path, 'r') as fd:
        assert fd.read() == 'a_value=test'


def test_should_create_directory_to_write_template(work_dir, valid_template_path):
    """
        Test create directory and write template
    """
    output_path = join(work_dir, 'a_dir', 'my_exe.sh')
    write_template(output_path, valid_template_path, given_data='test')

    assert exists(join(work_dir, 'a_dir'))
    assert exists(output_path)


def check_write_template_error_case(template_path: str, data: dict, exp_error: Exception):
    with TemporaryDirectory() as tmp_dir:
        output_path = join(tmp_dir, 'my_exe.sh')
        with pytest.raises(MlVToolException) as e:
            write_template(output_path, template_path, **data)
    assert isinstance(e.value.__cause__, exp_error)


def test_write_template_should_raise_if_template_does_not_exist(work_dir):
    """
        Test write_template raise an MlVToolException if the template file does not exist
    """
    template_path = join(work_dir, 'not_existing_template.tpl')
    check_write_template_error_case(template_path, data={}, exp_error=IOError)


def test_write_template_should_raise_if_template_format_error(work_dir):
    """
        Test write_template raise an MlVToolException if the template is wrongly formatted
    """
    template_data = 'a_value={{ t_data'
    template_path = join(work_dir, 'template_wrong_format.tpl')
    with open(template_path, 'w') as fd:
        fd.write(template_data)
    check_write_template_error_case(template_path, data={'t_data': 'test'}, exp_error=TemplateSyntaxError)


@pytest.mark.parametrize('missing_pattern', (('{{ printed_var }}',
                                              '{% for val in iterated_var %}{% endfor %}',
                                              '{{ accessed.var }}')))
def test_write_template_should_raise_if_missing_template_data(work_dir, missing_pattern):
    """
        Test write_template raise an MlVToolException if there is an undefined template variable
        Case of :
            - print
            - iteration
            - other access
    """
    template_data = f'a_value={missing_pattern}'
    template_path = join(work_dir, 'template.tpl')
    with open(template_path, 'w') as fd:
        fd.write(template_data)
    check_write_template_error_case(template_path, data={}, exp_error=UndefinedError)


def test_write_template_should_raise_if_can_not_write_executable_output(work_dir, mocker, valid_template_path):
    """
        Test write_template raise an MlVToolException if the executable output cannot be written
    """
    output_path = join(work_dir, 'output.sh')

    mocker.patch('builtins.open', side_effect=IOError)
    with pytest.raises(MlVToolException) as e:
        write_template(output_path, valid_template_path, given_data='test')
    assert isinstance(e.value.__cause__, IOError)


def test_should_write_formatted_python_script(work_dir):
    """
        Test write formatted and executable python script
    """
    script_content = 'my_var=4\nmy_list=[1,2,3]'
    script_path = join(work_dir, 'test.py')
    write_python_script(script_content, script_path)

    assert exists(script_path)
    assert stat.S_IMODE(os_stat(script_path).st_mode) == 0o755

    with open(script_path, 'r') as fd:
        assert fd.read() == 'my_var = 4\nmy_list = [1, 2, 3]\n'


def test_should_create_directory_to_write_formatted_python_script(work_dir):
    """
        Test create directory and write formatted and executable python script
    """
    script_content = 'my_var=4'
    script_path = join(work_dir, 'a_dir', 'test.py')
    write_python_script(script_content, script_path)

    assert exists(join(work_dir, 'a_dir'))
    assert exists(script_path)


def test_write_python_script_should_raise_if_cannot_write_executable_script(work_dir, mocker):
    """
        Test write_python_script raise an MlVToolException if can not write executable output
    """

    script_content = 'my_var=4\nmy_list=[1,2,3]'
    script_path = join(work_dir, 'test.py')

    mocker.patch('builtins.open', side_effect=IOError)
    with pytest.raises(MlVToolException) as e:
        write_python_script(script_content, script_path)
    assert isinstance(e.value.__cause__, IOError)


def test_write_python_script_should_raise_if_python_syntax_error(work_dir):
    """
        Test write_python_script raise an MlVToolException if python syntax error
    """

    script_content = 'my_var :=: 4'
    script_path = join(work_dir, 'test.py')

    with pytest.raises(MlVToolException) as e:
        write_python_script(script_content, script_path)
    assert isinstance(e.value.__cause__, SyntaxError)
