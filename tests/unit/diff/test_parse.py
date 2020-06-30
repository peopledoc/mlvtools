from os.path import join

import pytest

from mlvtools.diff.parse import get_ast, is_ast_equal, get_ast_from_file
from mlvtools.exception import MlVToolException


def test_should_parse_ast():
    """
       Tests should parse ast from string content
    """
    python_content = 'import os\nprint("hello")'
    assert get_ast(python_content)


def test_should_raise_if_wrong_format():
    """
        Test should raise if invalid syntax
    """
    with pytest.raises(MlVToolException) as e:
        get_ast('a:=3')
    assert isinstance(e.value.__cause__, SyntaxError)


def test_should_parse_ast_from_file(work_dir):
    """
       Tests should parse ast from string content
    """
    python_content = 'import os\nprint("hello")'
    script_path = join(work_dir, 'script.py')
    with open(script_path, 'w') as fd:
        fd.write(python_content)
    assert get_ast_from_file(script_path)


def test_should_raise_if_script_does_not_exist(work_dir):
    """
       Tests should raise if script does not exist
    """
    with pytest.raises(MlVToolException) as e:
        get_ast_from_file(join(work_dir, 'does_not_exist.py'))
    assert isinstance(e.value.__cause__, IOError)


@pytest.fixture
def script_base() -> str:
    python_content = """
# This is a comment
import os
from Typing import List

def list_dir(dir_path:str) -> List[str]:
    ''' A docstring '''
    return os.listdir(dir_path)

print('Hello !!')
print(list_dir('/tmp'))
"""
    return python_content


def get_script_base_spaces_and_blank() -> str:
    python_content = """
# This is a comment
import os
from Typing import List





def list_dir(dir_path:str) -> List[str]:
    ''' A docstring '''
    return os.listdir(dir_path)

print('Hello !!')
print(list_dir('/tmp'))
"""
    return python_content


def get_script_diff_comment() -> str:
    python_content = """
# This is a different comment
import os
from Typing import List

def list_dir(dir_path:str) -> List[str]:
    ''' A docstring '''
    # This a new comment
    return os.listdir(dir_path)

print('Hello !!')
print(list_dir('/tmp'))
"""
    return python_content


def get_script_diff_docstring() -> str:
    python_content = """
# This is a comment
import os
from Typing import List

def list_dir(dir_path:str) -> List[str]:
    ''' A different docstring '''
    return os.listdir(dir_path)

print('Hello !!')
print(list_dir('/tmp'))
"""
    return python_content


def get_script_diff() -> str:
    python_content = """
# This is a comment
import os
from Typing import List

def list_dir(dir_path:str) -> List[str]:
    ''' A docstring '''
    return dir_path

print('Hello !!')
print(list_dir('/tmp'))
"""
    return python_content


@pytest.mark.parametrize('diff_script_content', (get_script_base_spaces_and_blank(), get_script_diff_comment()))
def test_script_must_be_ast_equals(script_base, diff_script_content):
    """
        Test ast tree are equal even if diff on blank lines, whitespaces and comments
    """
    base_ast = get_ast(script_base)
    diff_ast = get_ast(diff_script_content)

    assert is_ast_equal(base_ast, diff_ast)


@pytest.mark.parametrize('diff_script_content', (get_script_diff_docstring(), get_script_diff()))
def test_script_must_not_be_ast_equals(script_base, diff_script_content):
    """
        Test ast tree are not equal if diff docstring or statements
    """
    base_ast = get_ast(script_base)
    diff_ast = get_ast(diff_script_content)

    assert not is_ast_equal(base_ast, diff_ast)
