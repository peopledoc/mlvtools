import ast
import logging
from collections import namedtuple

from docstring_parser import parse as dc_parse

from mlvtools.docstring_helpers.parse import resolve_docstring
from mlvtools.exception import MlVToolException


def extract_docstring(cell_content: str) -> str:
    """ Extract a docstring from a cell content """
    docstring = ''
    try:
        root = ast.parse(cell_content)
    except SyntaxError as e:
        raise MlVToolException(f'Invalid python cell format: {cell_content}') from e
    for node in ast.walk(root):
        if isinstance(node, ast.Module):
            docstring = ast.get_docstring(node)
            break
    return docstring


DocstringInfo = namedtuple('DocstringInfo',
                           ('method_name', 'docstring', 'repr', 'file_path'))


def extract_docstring_from_file(input_path: str, docstring_conf: dict = None) -> DocstringInfo:
    """
        Extract method docstring information (docstring, method_name, input_path)
        The provided python script must have one and only one method
        The extracted docstring is parsed and returned in docstring info
    """
    try:
        with open(input_path, 'r') as fd:
            root = ast.parse(fd.read())
    except FileNotFoundError as e:
        raise MlVToolException(
            f'Python input script {input_path} not found.') from e
    except SyntaxError as e:
        raise MlVToolException(f'Invalid python script format: {input_path}') from e

    for node in ast.walk(root):
        if isinstance(node, ast.FunctionDef):
            method_name = node.name
            docstring_str = ast.get_docstring(node)
            if docstring_conf:
                docstring_str = resolve_docstring(docstring_str, docstring_conf)
            docstring = dc_parse(docstring_str)
            break
    else:
        logging.error(f'Not method found in {input_path}')
        raise MlVToolException(f'Not method found in {input_path}')

    docstring_info = DocstringInfo(method_name=method_name,
                                   docstring=docstring,
                                   repr=docstring_str,
                                   file_path=input_path)
    return docstring_info
