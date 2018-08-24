import stat
import tempfile
from os import stat as os_stat
from os.path import realpath, dirname, join, exists
from uuid import uuid4

import pytest
from docstring_parser import parse as dc_parse

from mlvtool.exception import MlVToolException
from mlvtool.gen_dvc_step import get_import_line, DocstringInfo, get_info, \
    extract_docstring, gen_python_script, TEMPLATE_NAME

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
    """
        Test docstring extraction is resilient to an empty docstring
    """
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

    info = get_info(docstring_info, '/data/my_prj')

    expected_info = {
        'method_name': 'my_method',
        'import_line': 'from python.my_file import my_method',
        'arg_params': '',
        'params': []
    }

    assert info == expected_info


def test_should_extract_docstring_from_python_file():
    """
        Test docstring is extracted from python file with a unique method
    """
    file_docstring = '""" Not the docstring to extract """\n'
    docstring = '""" This is a docstring\n On multilines\n"""'
    with tempfile.TemporaryDirectory() as tmp:
        python_script = join(tmp, 'test.py')
        with open(python_script, 'w') as fd:
            fd.write(file_docstring)
            fd.write('import os\n')
            fd.write('def my_method():\n')
            fd.write(f'\t{docstring}\n')
            fd.write('\tpass')
        docstring_info = extract_docstring(python_script)
        assert docstring_info.file_path == python_script
        assert docstring_info.repr == 'This is a docstring\nOn multilines'
        assert docstring_info.method_name == 'my_method'
        assert docstring_info.docstring


def test_should_raise_if_file_not_found():
    """
        Test docstring extraction handle file not found
    """

    with pytest.raises(MlVToolException):
        extract_docstring(f'./{uuid4()}.py')


def test_should_raise_if_no_method_found():
    """
        Test docstring extraction  fail if no method found
    """
    file_docstring = '""" Not the docstring to extract """\n'
    with tempfile.TemporaryDirectory() as tmp:
        python_script = join(tmp, 'test.py')
        with open(python_script, 'w') as fd:
            fd.write(file_docstring)
            fd.write('import os\n')
        with pytest.raises(MlVToolException):
            extract_docstring(python_script)


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
                          template_path=TEMPLATE_NAME)
        assert exists(output_path)
        assert stat.S_IMODE(os_stat(output_path).st_mode) == 0o755
