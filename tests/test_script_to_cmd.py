import stat
import subprocess
import tempfile
from os import stat as os_stat
from os.path import realpath, dirname, join, exists

import pytest
from docstring_parser import parse as dc_parse

from mlvtool.exception import MlVToolException
from mlvtool.script_to_cmd import get_import_line, DocstringInfo, get_template_data, \
    gen_python_script, TEMPLATE_NAME, get_git_top_dir

CURRENT_DIR = realpath(dirname(__file__))


def test_should_return_git_top_dir():
    """
        Test a MlVTool message is raised if git command fail
    """
    assert subprocess.check_output(['which', 'git'])

    with tempfile.TemporaryDirectory() as tmp_dir:
        subprocess.check_output(['git', 'init'], cwd=tmp_dir)
        assert get_git_top_dir(tmp_dir) == tmp_dir


def test_should_raise_if_git_command_fail():
    """
        Test a MlVTool message is raised if git command fail
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        with pytest.raises(MlVToolException):
            get_git_top_dir(tmp_dir)


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

    info = get_template_data(docstring_info, '/data/my_prj')

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
    repr = ':param str param1: Param1 description\n' \
           ':param int param2:\n' \
           ':param param3: Param3 description\n' \
           ':param param4:\n'
    docstring_info = DocstringInfo(method_name='my_method',
                                   docstring=dc_parse(repr),
                                   repr=repr,
                                   file_path='/data/my_prj/python/my_file.py')

    info = get_template_data(docstring_info, '/data/my_prj')

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
    """
        Test docstring extraction is resilient to an empty docstring
    """
    file_path = '/data/my_prj/python/my_file.py'
    method_name = 'my_method'
    docstring_info = DocstringInfo(method_name,
                                   docstring=dc_parse(''),
                                   repr='',
                                   file_path=file_path)

    info = get_template_data(docstring_info, '/data/my_prj')

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

    info = get_template_data(docstring_info, '/data/my_prj')

    expected_info = {
        'method_name': 'my_method',
        'import_line': 'from python.my_file import my_method',
        'arg_params': '',
        'params': []
    }

    assert info == expected_info


def test_should_generate_a_python_cmd():
    docstring = '""" This is a docstring\n On multilines\n"""'
    with tempfile.TemporaryDirectory() as tmp:
        python_script = join(tmp, 'test.py')
        with open(python_script, 'w') as fd:
            fd.write('import os\n')
            fd.write('def my_method():\n')
            fd.write(f'\t{docstring}\n')
            fd.write('\tpass')

        output_path = join(tmp, 'out.py')
        gen_python_script(input_path=python_script,
                          output_path=output_path,
                          src_dir=tmp,
                          template_name=TEMPLATE_NAME)
        assert exists(output_path)
        assert stat.S_IMODE(os_stat(output_path).st_mode) == 0o755
