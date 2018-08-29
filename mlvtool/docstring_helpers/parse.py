from docstring_parser import parse as dc_parse
from docstring_parser.parser import Docstring, ParseError

from mlvtool.exception import MlVToolException


def parse_docstring(docstring_str: str) -> Docstring:
    try:
        docstring = dc_parse(docstring_str.replace('\t', ''))
    except ParseError as e:
        raise MlVToolException(f'Docstring format error. {e}') from e
    return docstring
