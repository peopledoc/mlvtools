import tempfile
from os.path import join
from uuid import uuid4

import pytest

from mlvtool.docstring_helpers.extract import extract_docstring_from_file, extract_docstring
from mlvtool.exception import MlVToolException


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
        docstring_info = extract_docstring_from_file(python_script)
        assert docstring_info.file_path == python_script
        assert docstring_info.repr == 'This is a docstring\nOn multilines'
        assert docstring_info.method_name == 'my_method'
        assert docstring_info.docstring


def test_should_raise_if_file_not_found():
    """
        Test docstring extraction handle file not found
    """

    with pytest.raises(MlVToolException) as e:
        extract_docstring_from_file(f'./{uuid4()}.py')
    assert isinstance(e.value.__cause__, FileNotFoundError)


def test_should_raise_if_no_method_found():
    """
        Test docstring extraction fail if no method found
    """
    file_docstring = '""" Not the docstring to extract """\n'
    with tempfile.TemporaryDirectory() as tmp:
        python_script = join(tmp, 'test.py')
        with open(python_script, 'w') as fd:
            fd.write(file_docstring)
            fd.write('import os\n')
        with pytest.raises(MlVToolException):
            extract_docstring_from_file(python_script)


def test_should_raise_if_syntax_error():
    """
        Test docstring extraction fail if python script syntax error
    """
    with tempfile.TemporaryDirectory() as tmp:
        python_script = join(tmp, 'test.py')
        with open(python_script, 'w') as fd:
            fd.write('import os\n')
            fd.write('def my_method(my-param):\n')
            fd.write('pass\n')
        with pytest.raises(MlVToolException) as e:
            extract_docstring_from_file(python_script)
        assert isinstance(e.value.__cause__, SyntaxError)


def test_should_extract_docstring():
    """
        Test that different docstring format are well extracted
    """

    docstring_cell = '# Some comments\n' \
                     '"""{}"""\n' \
                     'code = \'some code\'' \
                     '# And comment'

    inline_docstring = 'An inline docstring'
    docstring = extract_docstring(docstring_cell.format(inline_docstring))
    assert docstring == inline_docstring

    inline_docstring = 'An inline docstring """ aa """ invalid'
    with pytest.raises(MlVToolException) as e:
        extract_docstring(docstring_cell.format(inline_docstring))
    assert isinstance(e.value.__cause__, SyntaxError)

    for multi_line in ('\n{}\n', '{}\n', '\n{}'):
        multiline_docstring = multi_line.format('A multiline docstring'
                                                '\nWithout param info\n')
        docstrings = extract_docstring(
            docstring_cell.format(multiline_docstring))
        assert docstrings == multiline_docstring.strip()

    multiline_docstring = 'A multiline\n docstring """\naa= ' \
                          '= 4\n""" invalid'
    with pytest.raises(MlVToolException) as e:
        extract_docstring(docstring_cell.format(multiline_docstring))
    assert isinstance(e.value.__cause__, SyntaxError)
