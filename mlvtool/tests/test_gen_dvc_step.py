from os.path import realpath, dirname

import pytest
from docstring_parser import parse as dc_parse

from mlvtool.gen_dvc_step import get_import_line, DocstringInfo, get_info

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
    file_path = '/data/my_prj/python/my_file.py'
    method_name = 'my_method'
    repr = '     :param str param1: Param1 description\n' \
           '     :param int param2:\n' \
           '     :param param3: Param3 description\n' \
           '     :param param4:\n'
    docstring_info = DocstringInfo(method_name,
                                   docstring=dc_parse(repr),
                                   repr=repr,
                                   file_path=file_path)

    info = get_info(docstring_info, '/data/my_prj')

    expected_info = {
        'method_name': 'my_method',
        'import_line': 'from python.my_file import my_method',
        'arg_params': 'args.param1, args.param2, args.param3, args.param4',
        'params': [
            {
                'name': 'param1',
                'type': 'str',
                'help': 'Param1 description'
            },
            {
                'name': 'param2',
                'type': 'int',
                'help': ''
            },
            {
                'name': 'param3',
                'type': None,
                'help': 'Param3 description'
            },
            {
                'name': 'param4',
                'type': None,
                'help': ''
            }
        ]
    }

    assert info == expected_info


def test_should_handle_empty_docstring():
    file_path = '/data/my_prj/python/my_file.py'
    method_name = 'my_method'
    docstring_info = DocstringInfo(method_name,
                                   docstring=dc_parse(''),
                                   repr='',
                                   file_path=file_path)

    info = get_info(docstring_info, '/data/my_prj')

    expected_info = {
        'method_name': 'my_method',
        'import_line': 'from python.my_file import my_method',
        'arg_params': '',
        'params': []
    }

    assert info == expected_info


def test_should_handle_docstring_without_param():
    file_path = '/data/my_prj/python/my_file.py'
    method_name = 'my_method'
    repr = '     A description\n' \
           '     :return plop:\n'
    docstring_info = DocstringInfo(method_name,
                                   docstring=dc_parse(repr),
                                   repr=repr,
                                   file_path=file_path)

    info = get_info(docstring_info, '/data/my_prj')

    expected_info = {
        'method_name': 'my_method',
        'import_line': 'from python.my_file import my_method',
        'arg_params': '',
        'params': []
    }

    assert info == expected_info
