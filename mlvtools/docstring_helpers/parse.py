from collections import namedtuple
from typing import Dict, List, Optional

import jinja2
from docstring_parser import parse as dc_parse
from docstring_parser.parser import Docstring, ParseError

from mlvtools.exception import MlVToolException
from mlvtools.helper import render_string_template


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
                                   f'Expected :dvc-extra: {{python_other_param}}')
        if args[0] != DocstringDvcExtra.DVC_EXTRA_KEY:
            raise MlVToolException(f'Receive bad parameter for {DocstringDvcExtra.DVC_EXTRA_KEY} {args[0]}')
        return DocstringDvcExtra(description)


class DocstringDvcMetaFile:
    DVC_META_FILE_KEY = 'dvc-meta-file'
    """
        Syntax
        [:dvc-meta-file: {meta_file_name}]?

        :dvc-meta-file: pipeline.dvc
    """

    def __init__(self, file_name: str):
        self.file_name = file_name

    @staticmethod
    def from_meta(args: List[str], description: str) -> 'DocstringDvcMetaFile':
        if len(args) != 1 or not description:
            raise MlVToolException(f'Docstring dvc-meta-file invalid syntax: {args}:{description}.'
                                   f'Expected :dvc-meta-file: {{meta_file_name}}')
        if args[0] != DocstringDvcMetaFile.DVC_META_FILE_KEY:
            raise MlVToolException(f'Receive bad parameter for {DocstringDvcMetaFile.DVC_META_FILE_KEY} {args[0]}')
        description = description if description.endswith('.dvc') else f'{description}.dvc'
        return DocstringDvcMetaFile(description)


class DocstringDvcCommand:
    DVC_CMD_KEY = 'dvc-cmd'
    """
        Syntax
        :dvc-cmd: {dvc_command}

        dvc-cmd: dvc run -o ./out_train.csv -o ./out_test.csv ./py_cmd -m train --out ./out_train.csv

    """

    def __init__(self, cmd: str):
        self.cmd = cmd

    @staticmethod
    def from_meta(args: List[str], description: str) -> 'DocstringDvcCommand':
        if len(args) != 1 or not description:
            raise MlVToolException(f'Docstring dvc-cmd invalid syntax: {args}:{description}.'
                                   f'Expected :dvc-cmd: {{dvc_command}}')
        if args[0] != DocstringDvcCommand.DVC_CMD_KEY:
            raise MlVToolException(f'Receive bad parameter for {DocstringDvcCommand.DVC_CMD_KEY} {args[0]}')
        return DocstringDvcCommand(description)


DvcParams = namedtuple('DvcParams', ('dvc_in', 'dvc_out', 'dvc_extra', 'dvc_cmd', 'meta_file_name'))


def get_dvc_params(docstring: Docstring) -> DvcParams:
    """
        Return a set of dvc docstring parameters
        (dvc dependencies, outputs, extra parameters or whole command)
    """
    dvc_in = []
    dvc_out = []
    dvc_extra = []
    dvc_cmd = []
    params = {param.arg_name: param.type_name for param in docstring.params}
    dvc_meta = None
    for meta in docstring.meta:
        if not meta.args:
            continue
        if meta.args[0] == DocstringDvcIn.DVC_IN_KEY:
            dvc_in.append(DocstringDvcIn.from_meta(params, meta.args, meta.description))
        elif meta.args[0] == DocstringDvcOut.DVC_OUT_KEY:
            dvc_out.append(DocstringDvcOut.from_meta(params, meta.args, meta.description))
        elif meta.args[0] == DocstringDvcExtra.DVC_EXTRA_KEY:
            dvc_extra.append(DocstringDvcExtra.from_meta(meta.args, meta.description))
        elif meta.args[0] == DocstringDvcMetaFile.DVC_META_FILE_KEY:
            dvc_meta = DocstringDvcMetaFile.from_meta(meta.args, meta.description)
        elif meta.args[0] == DocstringDvcCommand.DVC_CMD_KEY:
            dvc_cmd.append(DocstringDvcCommand.from_meta(meta.args, meta.description))
    if len(dvc_cmd) > 1:
        raise MlVToolException(f'Only one occurence of {DocstringDvcCommand.DVC_CMD_KEY} is allowed')
    if dvc_cmd and (dvc_in or dvc_out or dvc_extra):
        raise MlVToolException(f'Dvc command {DocstringDvcCommand.DVC_CMD_KEY} is exclusive with other dvc parameters '
                               f'[{DocstringDvcExtra.DVC_EXTRA_KEY}, {DocstringDvcIn.DVC_IN_KEY}, '
                               f'{DocstringDvcOut.DVC_OUT_KEY}]')

    return DvcParams(dvc_in, dvc_out, dvc_extra, dvc_cmd[0] if dvc_cmd else '', dvc_meta.file_name if dvc_meta else '')


def parse_docstring(docstring_str: str) -> Docstring:
    try:
        docstring = dc_parse(docstring_str)
    except ParseError as e:
        raise MlVToolException(f'Docstring format error. {e}') from e
    return docstring


def resolve_docstring(docstring: str, docstring_conf: dict) -> str:
    """
        Use jinja to resolve docstring template using user custom configuration
    """
    try:
        return render_string_template(docstring, conf=docstring_conf)
    except jinja2.exceptions.TemplateError as e:
        raise MlVToolException(f'Cannot resolve docstring using Jinja, {e}') from e
