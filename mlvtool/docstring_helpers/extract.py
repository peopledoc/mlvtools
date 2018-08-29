import ast
import logging
from collections import namedtuple
from typing import List

from docstring_parser import parse as dc_parse

from mlvtool.exception import MlVToolException


def extract_docstring(cell_content: str) -> List[str]:
    """ Extract a docstring from a cell content """
    recording = False
    docstrings = []
    # TODO improve docstrings extraction
    for line in cell_content.split('\n'):
        nb_occ_separator = line.count('"""')
        line = line.strip()
        if nb_occ_separator:
            # Inline specific case
            if (not recording and docstrings) or nb_occ_separator > 2:
                raise MlVToolException(
                    f'Only one docstrings allowed in first Notebook cell, '
                    f'{len(docstrings)} found')
            if nb_occ_separator == 2:
                docstrings.append(line)
                continue
            recording = not recording
            docstrings.append(line)
        elif recording:
            docstrings.append(line)
    return docstrings


DocstringInfo = namedtuple('DocstringInfo',
                           ('method_name', 'docstring', 'repr', 'file_path'))


def extract_docstring_from_file(input_path: str) -> DocstringInfo:
    try:
        with open(input_path, 'r') as fd:
            root = ast.parse(fd.read())
    except FileNotFoundError as e:
        raise MlVToolException(
            f'Python input script {input_path} not found.') from e
    for node in ast.walk(root):
        if isinstance(node, ast.FunctionDef):
            method_name = node.name
            docstring_str = ast.get_docstring(node)
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
