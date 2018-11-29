from os.path import realpath, dirname, join, exists

import pytest
from pytest import fixture

from mlvtools.conf.conf import MlVToolConf
from mlvtools.docstring_helpers.parse import parse_docstring
from mlvtools.exception import MlVToolException
from mlvtools.ipynb_to_python import export_to_script, get_param_as_python_method_format, filter_no_effect, \
    get_data_from_docstring, get_arguments_from_docstring, get_arguments_as_param, get_docstring_data, DocstringWrapper
from tests.helpers.utils import gen_notebook, to_notebook_code_cell

CURRENT_DIR = realpath(dirname(__file__))


@fixture
def conf():
    return MlVToolConf(top_directory='./')


def test_should_convert_notebook_to_python_script(conf, work_dir):
    """
        Test Notebook is converted to python script
    """
    output_path = join(work_dir, 'out.py')
    notebook_path = gen_notebook(cells=['print(\'poney\')'], tmp_dir=work_dir,
                                 file_name='test.ipynb', docstring=None)
    export_to_script(input_notebook_path=notebook_path, output_path=output_path, conf=conf)

    assert exists(output_path)
    with open(output_path, 'r') as fd:
        content = fd.read()

    # Check main method is created
    assert 'def mlvtools_test():' in content


@pytest.mark.parametrize('header', (None, '#Big Title'))
def test_should_detect_parameters(header, conf, work_dir):
    """
        Test Notebook is converted to parameterized python script,
        parameter cell in Notebook is detected and well handled.
        The parameter cell must be the first code cell. It should be detected
        if there is a markdown header or not.
    """
    output_path = join(work_dir, 'out.py')

    docstring_cell = '''
# Parameters
"""
    :param str subset: The kind of subset to generate.
    :param int rate: The rate of I don't know what
    :param param3:
"""
subset = 'train'
toto = 12
        '''
    notebook_path = gen_notebook(cells=['print(\'poney\')'], tmp_dir=work_dir,
                                 file_name='test.ipynb',
                                 docstring=docstring_cell,
                                 header=header)
    export_to_script(input_notebook_path=notebook_path, output_path=output_path, conf=conf)
    assert exists(output_path)
    with open(output_path, 'r') as fd:
        content = fd.read()

    # Check main method is created
    assert 'def mlvtools_test(subset: str, rate: int, param3):' in content


def test_should_raise_if_invalid_docstring(conf, work_dir):
    """
        Test an MlVTool exception is raised if docstring is invalid
    """

    output_path = join(work_dir, 'out.py')

    docstring_cell = '''
    # Parameters
    """
        :param param3
    """
    subset = 'train'
    toto = 12
    '''

    notebook_path = gen_notebook(cells=['print(\'poney\')'], tmp_dir=work_dir,
                                 file_name='test.ipynb',
                                 docstring=docstring_cell)
    with pytest.raises(MlVToolException):
        export_to_script(input_notebook_path=notebook_path, output_path=output_path, conf=conf)


def test_should_raise_if_more_than_one_docstring_in_first_cell(conf, work_dir):
    """
        Test multi docstring in the parameter cell is detected
    """
    output_path = join(work_dir, 'out.py')

    docstring_cell = '''
    # Parameters
    """
        :param param3: Plop
    """
     """
        :param param6: AA
    """
    subset = 'train'
    toto = 12
    '''

    notebook_path = gen_notebook(cells=['print(\'poney\')'], tmp_dir=work_dir,
                                 file_name='test.ipynb',
                                 docstring=docstring_cell)
    with pytest.raises(MlVToolException):
        export_to_script(input_notebook_path=notebook_path, output_path=output_path, conf=conf)


def test_should_be_resilient_to_empty_notebook(conf, work_dir):
    """
        Test templating is resilient to empty Notebook, no exception.
    """
    output_path = join(work_dir, 'out.py')
    notebook_path = gen_notebook(cells=['print(\'poney\')'], tmp_dir=work_dir,
                                 file_name='test.ipynb', docstring=None)
    export_to_script(input_notebook_path=notebook_path, output_path=output_path, conf=conf)
    assert exists(output_path)


def test_should_extract_parameters_as_python_params():
    """
        Test parameters are extracted from docstring and converted to python format
    """

    docstring_str = '''"""
    :param str param_one: Param1 description
    :param int param2:
    :param param3: Param3 description
    :param param4:
    """'''
    parameters = get_param_as_python_method_format(parse_docstring(docstring_str))

    assert parameters == 'param_one: str, param2: int, param3, param4'


def test_should_extract_parameters_as_python_command_line_arguments():
    """
        Test parameters are extracted from docstring and converted to python command line argument
    """

    docstring_str = '''"""
    :param str param_one: Param1 description
    """'''
    docstring, _ = get_docstring_data(docstring_str)
    arguments = get_arguments_from_docstring(docstring)

    assert arguments == [
        {
            'name': 'param-one',
            'type': 'str',
            'help': 'Param1 description',
            'is_list': False
        }]


def test_should_extract_arguments_as_parameters():
    """
        Test get argument as parameters for python method call
    """
    docstring_str = '''"""
    :param str param_one: Param1 description
    :param int param2:
    """'''
    args_as_param = get_arguments_as_param(parse_docstring(docstring_str))

    assert args_as_param == 'args.param_one, args.param2'


def test_should_convert_list_param_to_python_arg():
    """
        Test convert list param to python arg
    """
    repr = ':param list param_one: Param1 description\n'
    arguments = get_arguments_from_docstring(parse_docstring(repr))

    assert arguments == [{'name': 'param-one',
                          'type': 'str',
                          'help': 'Param1 description',
                          'is_list': True
                          }]


def test_should_not_raise_if_empty_docstring():
    """
        Test do not raise if first code cell with empty docstring
    """
    first_code_cell = f'''
# Some comments
code = 'some code again'
# And comment
    '''
    docstring_wrapper = get_data_from_docstring([to_notebook_code_cell(first_code_cell)])

    assert docstring_wrapper == DocstringWrapper(docstring='', params='', arguments=[], arg_params='')


def test_should_not_raise_if_no_param_in_docstring():
    """
        Test do not raise if no param in docstring
    """
    docstring = '''"""
Docstring without param
"""'''
    first_code_cell = f'''
# Some comments
{docstring}
code = 'some code again'
# And comment
    '''

    docstring_wrapper = get_data_from_docstring([to_notebook_code_cell(first_code_cell)])

    assert docstring_wrapper == DocstringWrapper(docstring=docstring, params='', arguments=[], arg_params='')


def test_should_extract_docstring_and_params():
    """
        Test docstring and parameters are well extracted
    """
    docstring = '''"""
:param str param_one: Param1 description
:param int param2:
:param param3: Param3 description
:param param4:
"""'''
    docstring_cell = f'''
# Some comments
{docstring}
code = 'some code again'
# And comment
    '''
    docstring_wrapper = get_data_from_docstring([to_notebook_code_cell(docstring_cell)])
    expected_arguments = [
        {
            'name': 'param-one',
            'type': 'str',
            'help': 'Param1 description',
            'is_list': False
        },
        {
            'name': 'param2',
            'type': 'int',
            'help': '',
            'is_list': False
        },
        {
            'name': 'param3',
            'type': None,
            'help': 'Param3 description',
            'is_list': False
        },
        {
            'name': 'param4',
            'type': None,
            'help': '',
            'is_list': False
        }
    ]

    assert docstring_wrapper.params == 'param_one: str, param2: int, param3, param4'
    assert docstring_wrapper.docstring == docstring.strip('\n')
    assert docstring_wrapper.arguments == expected_arguments
    assert docstring_wrapper.arg_params == 'args.param_one, args.param2, args.param3, args.param4'


def test_should_discard_cell():
    """
        Test that cell containing #No effect statement are discarded
    """
    standard_cell = '''
    #This is a comment but not a No effect
    value = 15
    '''
    assert filter_no_effect(standard_cell, {}) == standard_cell

    no_effect_cell = '''
    #This is a comment but not a No effect
    # No effect
    big_res = big_call()
    '''
    assert filter_no_effect(no_effect_cell, {'ignore_keys': '# No effect'}) == ''
