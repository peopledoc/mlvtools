from typing import Dict, List, Tuple, Optional

from docstring_parser import parse as dc_parse
from docstring_parser.parser import Docstring, ParseError

from mlvtool.exception import MlVToolException


class DocstringDvc:
    """
        Syntax
        :dvc-[in|out] [{related_param}]?: {{file_path}}
    """

    def __init__(self, file_path: str, related_param: str = None):
        self.related_param = related_param
        self.file_path = file_path

    def __eq__(self, other):
        return self.file_path == other.file_path and \
               self.related_param == other.related_param

    @staticmethod
    def meta_checks(params: Dict[str, Optional[str]], args: List[str], description: str, expected_key: str):
        if len(args) == 0:
            raise MlVToolException('Cannot parse empty DocstringDVC')
        if len(args) > 2:
            raise MlVToolException(f'Invalid syntax: {args}. Expected :dvc-[in|out] [related_param]?: {{file_path}}')
        if args[0] != expected_key:
            raise MlVToolException('Receive bad parameter {}'.format(args[0]))

        if not description:
            raise MlVToolException(f'Not path given for {args}')

        related_param = args[1] if len(args) == 2 else None

        if related_param and related_param not in params:
            raise MlVToolException(f'Cannot find related parameter for {related_param} in {args}')

        if related_param and params[related_param] not in (None, 'str'):
            raise MlVToolException(f'Unsupported type {params[related_param]} for {args}. Discard.')


class DocstringDvcIn(DocstringDvc):
    DVC_IN_KEY = 'dvc-in'

    """
        Syntax
        :dvc-in param2: path/to/in/file
        :dvc-in: path/to/other/infile.test
    """

    def __init__(self, path: str, related_param: str = None):
        super().__init__(path, related_param)

    @staticmethod
    def from_meta(params: Dict[str, Optional[str]], args: List[str], description: str) -> 'DocstringDvcIn':
        DocstringDvc.meta_checks(params, args, description, DocstringDvcIn.DVC_IN_KEY)
        return DocstringDvcIn(description, args[1] if len(args) == 2 else None)


class DocstringDvcOut(DocstringDvc):
    DVC_OUT_KEY = 'dvc-out'
    """
        Syntax
        :dvc-out: path/to/file.txt
        :dvc-out param1: path/to/other
    """

    def __init__(self, path: str, related_param: str = None):
        super().__init__(path, related_param)

    @staticmethod
    def from_meta(params: Dict[str, Optional[str]], args: List[str], description: str) -> 'DocstringDvcOut':
        DocstringDvc.meta_checks(params, args, description, DocstringDvcOut.DVC_OUT_KEY)
        return DocstringDvcOut(description, args[1] if len(args) == 2 else None)


class DocstringDvcExtra:
    DVC_EXTRA_KEY = 'dvc-extra'
    """
        Syntax
        [:dvc-extra: {python_other_param}]?

        :dvc-extra: --mode train --rate 12
    """

    def __init__(self, extra: str):
        self.extra = extra

    @staticmethod
    def from_meta(args: List[str], description: str) -> 'DocstringDvcExtra':
        if len(args) != 1 or not description:
            raise MlVToolException(f'Docstring dvc-extra invalid syntax: {args}:{description}.'
                                   f'Expected [:dvc-extra: {{python_other_param}}]?')
        if args[0] != DocstringDvcExtra.DVC_EXTRA_KEY:
            raise MlVToolException('Receive bad parameter for dvc-extra {}'.format(args[0]))
        return DocstringDvcExtra(description)


def get_dvc_params(docstring: Docstring) -> Tuple[List[DocstringDvcIn], List[DocstringDvcOut], List[DocstringDvcExtra]]:
    dvc_in = []
    dvc_out = []
    dvc_extra = []
    params = {param.arg_name: param.type_name for param in docstring.params}
    for meta in docstring.meta:
        if not meta.args:
            continue
        if meta.args[0] == DocstringDvcIn.DVC_IN_KEY:
            dvc_in.append(DocstringDvcIn.from_meta(params, meta.args, meta.description))
        elif meta.args[0] == DocstringDvcOut.DVC_OUT_KEY:
            dvc_out.append(DocstringDvcOut.from_meta(params, meta.args, meta.description))
        elif meta.args[0] == DocstringDvcExtra.DVC_EXTRA_KEY:
            dvc_extra.append(DocstringDvcExtra.from_meta(meta.args, meta.description))
    return dvc_in, dvc_out, dvc_extra


def parse_docstring(docstring_str: str) -> Docstring:
    try:
        docstring = dc_parse(docstring_str.replace('\t', ''))
    except ParseError as e:
        raise MlVToolException(f'Docstring format error. {e}') from e
    return docstring
