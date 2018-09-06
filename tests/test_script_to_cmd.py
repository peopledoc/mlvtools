from os.path import realpath, dirname

import pytest
from docstring_parser import parse as dc_parse

from mlvtools.script_to_cmd import get_import_line, DocstringInfo, get_py_template_data, \
    get_dvc_template_data

CURRENT_DIR = realpath(dirname(__file__))


def test_should_return_import_line():
    """
        Test return an import line relative to the provided  python source
        directory
    """
    script_path = '/data/prj/code/python/script/auto/my_script.py'
    python_src_dir = '/data/prj/code/python/'
    import_line = get_import_line(script_path, python_src_dir,
                                  method_name='my_method')
    assert import_line == 'from script.auto.my_script import my_method'


def test_should_fail_in_incoherent_import():
    """
        Test raise if inconsistent python source directory
    """
    script_path = '/data/code/python/script/auto/my_script.py'
    python_src_dir = '/data/prj/'
    with pytest.raises(Exception):
        get_import_line(script_path, python_src_dir, method_name='my_method')


def test_should_get_docstring_info():
    """
        Test info are extracted from docstring
    """
    file_path = '/data/my_prj/python/my_file.py'
    method_name = 'my_method'
    repr = 'Some description'
    docstring_info = DocstringInfo(method_name,
                                   docstring=dc_parse(repr),
                                   repr=repr,
                                   file_path=file_path)

    info = get_py_template_data(docstring_info, '/data/my_prj')

    expected_info = {
        'method_name': 'my_method',
        'import_line': 'from python.my_file import my_method',
        'arg_params': '',
        'params': []
    }

    assert info == expected_info


def test_should_get_docstring_python_script_param():
    """
        Test python parameters are extracted from docstring
    """
    repr = ':param str param_one: Param1 description\n' \
           ':param int param2:\n' \
           ':param param3: Param3 description\n' \
           ':param param4:\n'
    docstring_info = DocstringInfo(method_name='my_method',
                                   docstring=dc_parse(repr),
                                   repr=repr,
                                   file_path='/data/my_prj/python/my_file.py')

    info = get_py_template_data(docstring_info, '/data/my_prj')

    expected_info = {
        'method_name': 'my_method',
        'import_line': 'from python.my_file import my_method',
        'arg_params': 'args.param_one, args.param2, args.param3, args.param4',
        'params': [
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
    }
    assert info == expected_info


def test_should_convert_list_param_to_python_arg():
    """
        Test convert list param to python arg
    """
    repr = ':param list param_one: Param1 description\n'
    docstring_info = DocstringInfo(method_name='my_method',
                                   docstring=dc_parse(repr),
                                   repr=repr,
                                   file_path='/data/my_file.py')
    info = get_py_template_data(docstring_info, '/data')
    assert info['params'] == [{'name': 'param-one',
                               'type': 'str',
                               'help': 'Param1 description',
                               'is_list': True
                               }]


def test_should_get_dvc_param_from_docstring():
    """Test dvc parameters are extracted from docstring"""
    repr = ':param str param-one: Param1 description\n' \
           ':param param2: input file\n' \
           ':dvc-out: path/to/file.txt\n' \
           ':dvc-out param-one: path/to/other\n' \
           ':dvc-in param2: path/to/in/file\n' \
           ':dvc-in: path/to/other/infile.test\n' \
           ':dvc-extra: --train --rate 12'
    docstring_info = DocstringInfo(method_name='my_method',
                                   docstring=dc_parse(repr),
                                   repr=repr,
                                   file_path='/data/my_prj/python/my_file.py')
    python_cmd_path = '/script/python/test_cmd'
    info = get_dvc_template_data(docstring_info, python_cmd_path)

    expected_info = {
        'variables': ['PARAM2="path/to/in/file"', 'PARAM_ONE="path/to/other"'],
        'dvc_inputs': ['$PARAM2', 'path/to/other/infile.test'],
        'dvc_outputs': ['path/to/file.txt', '$PARAM_ONE'],
        'python_params': '--param2 $PARAM2 --param-one $PARAM_ONE --train --rate 12',
        'python_script': python_cmd_path
    }
    assert expected_info.keys() == info.keys()

    assert sorted(expected_info['variables']) == sorted(info['variables'])
    assert sorted(expected_info['dvc_inputs']) == sorted(info['dvc_inputs'])
    assert sorted(expected_info['dvc_outputs']) == sorted(info['dvc_outputs'])
    assert sorted(expected_info['python_params'].split(' ')) == sorted(info['python_params'].split(' '))
    assert expected_info['python_script'] == info['python_script']


def test_should_get_dvc_cmd_param_from_docstring():
    """Test dvc parameters are extracted from docstring"""
    cmd = 'dvc run -o ./out_train.csv \n' \
          '-o ./out_test.csv\n' \
          './py_cmd -m train --out ./out_train.csv &&\n' \
          './py_cmd -m test --out ./out_test.csv'
    repr = ':param str param-one: Param1 description\n' \
           ':param param2: input file\n' \
           f':dvc-cmd: {cmd}'
    docstring_info = DocstringInfo(method_name='my_method',
                                   docstring=dc_parse(repr),
                                   repr=repr,
                                   file_path='/data/my_prj/python/my_file.py')
    python_cmd_path = '../script/python/test_cmd'
    info = get_dvc_template_data(docstring_info, python_cmd_path)

    assert len(info.keys()) == 1
    assert info['whole_command'] == cmd.replace('\n', ' \\\n')


def test_should_handle_empty_docstring():
    """
        Test docstring extraction is resilient to an empty docstring
    """
    file_path = '/data/my_prj/python/my_file.py'
    method_name = 'my_method'
    docstring_info = DocstringInfo(method_name,
                                   docstring=dc_parse(''),
                                   repr='',
                                   file_path=file_path)

    info = get_py_template_data(docstring_info, '/data/my_prj')

    expected_info = {
        'method_name': 'my_method',
        'import_line': 'from python.my_file import my_method',
        'arg_params': '',
        'params': []
    }

    assert info == expected_info


def test_should_handle_docstring_without_param():
    """
        Test docstring extraction is resilient to a no param docstring
    """
    file_path = '/data/my_prj/python/my_file.py'
    method_name = 'my_method'
    repr = '     A description\n' \
           '     :return plop:\n'
    docstring_info = DocstringInfo(method_name,
                                   docstring=dc_parse(repr),
                                   repr=repr,
                                   file_path=file_path)

    info = get_py_template_data(docstring_info, '/data/my_prj')

    expected_info = {
        'method_name': 'my_method',
        'import_line': 'from python.my_file import my_method',
        'arg_params': '',
        'params': []
    }

    assert info == expected_info
