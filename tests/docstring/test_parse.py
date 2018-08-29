import pytest
from docstring_parser import ParseError

from mlvtool.docstring_helpers.parse import parse_docstring
from mlvtool.exception import MlVToolException


def test_should_parse_docstring():
    """
        Test parse valid docstring
    """

    docstring_str = '''
    A multiline docstring
    :param p1:
    '''
    docstring = parse_docstring(docstring_str)
    assert docstring


def test_should_raise_if_format_error():
    """
        Test exception is raised if docstring syntax error
    """
    docstring_error = '''
    :param p1
    '''
    with pytest.raises(MlVToolException) as e:
        parse_docstring(docstring_error)
    assert isinstance(e.value.__cause__, ParseError)
