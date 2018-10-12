#!/usr/bin/env python3
import argparse
import logging
from collections import namedtuple
from os import makedirs, chmod
from os.path import abspath, exists
from os.path import realpath, dirname, join
from typing import List, Tuple

from docstring_parser.parser import Docstring
from nbconvert import PythonExporter
from nbformat import NotebookNode

from mlvtools.cmd import CommandHelper, ArgumentBuilder
from mlvtools.conf.conf import get_script_output_path, load_conf_or_default, MlVToolConf, get_conf_file_default_path, \
    DEFAULT_IGNORE_KEY, get_work_directory
from mlvtools.docstring_helpers.extract import extract_docstring
from mlvtools.docstring_helpers.parse import parse_docstring
from mlvtools.exception import MlVToolException
from mlvtools.helper import to_method_name, extract_type, to_cmd_param

logging.getLogger().setLevel(logging.INFO)
CURRENT_DIR = realpath(dirname(__file__))
TEMPLATE_PATH = join(CURRENT_DIR, '..', 'template', 'ml-python.tpl')

DocstringWrapper = namedtuple('DocstringWrapper',
                              ('docstring', 'params', 'arguments', 'arg_params'))


def get_config(template_path: str) -> dict:
    return {'TemplateExporter': {'template_file': template_path},
            'NbConvertApp': {'export_format': 'python'}}


def export(input_notebook_path: str, output_path: str, conf: MlVToolConf):
    """
        Export a    notebook to a parameterize Python 3 script
        using jinja templates
    """
    exporter = PythonExporter(get_config(TEMPLATE_PATH))
    exporter.register_filter(name='filter_no_effect',
                             jinja_filter=filter_no_effect)
    exporter.register_filter(name='get_data_from_docstring',
                             jinja_filter=get_data_from_docstring)
    exporter.register_filter(name='sanitize_method_name',
                             jinja_filter=to_method_name)
    resources = {'ignore_keys': conf.ignore_keys}
    try:
        output_script, _ = exporter.from_filename(input_notebook_path, resources=resources)
    except Exception as e:
        raise MlVToolException(e) from e

    if not output_script:
        logging.warning('Empty notebook provided. Nothing to do.')
        return
    makedirs(dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as fd:
        fd.write(output_script)
    chmod(output_path, 0o755)


def get_arguments_from_docstring(docstring_data: Docstring) -> list:
    """
        Extract Python command line arguments from docstring
    """

    if not docstring_data.params:
        logging.warning('No params found.')

    arguments_params = []
    for param in docstring_data.params:
        type_info = extract_type(param.type_name)
        arguments_params.append({'name': to_cmd_param(param.arg_name),
                                 'type': type_info.type_name,
                                 'help': param.description,
                                 'is_list': type_info.is_list})
    return arguments_params


def get_arguments_as_param(docstring_data: Docstring) -> str:
    """
        Get formatted parameter for python method call
    """
    return ', '.join([f'args.{arg.arg_name}' for arg in docstring_data.params])


def get_param_as_python_method_format(docstring_data: Docstring) -> str:
    """
        Extract parameters from a docstring then format them
    """
    params = ['{}{}'.format(p.arg_name, '' if not p.type_name else f': {p.type_name}')
              for p in docstring_data.params]
    return ', '.join(params)


def get_docstring_data(cell_content: str) -> Tuple[Docstring, str]:
    """
        Extract docstring and formatted parameters from a cell content
    """
    docstring_str = extract_docstring(cell_content)
    if docstring_str:
        return parse_docstring(docstring_str), f'"""\n{docstring_str}\n"""'
    logging.warning("Docstring not found.")
    return Docstring(), ''


def get_data_from_docstring(cells: List[NotebookNode]):
    """
        Extract parameters from the first code cell and remove it
    """
    try:
        first_code_cell = next(cell for cell in cells if is_code_cell(cell))
    except StopIteration:
        logging.warning('No code cell found.')
        return DocstringWrapper('', '', [], '')
    docstring_data, docstring_str = get_docstring_data(first_code_cell.source)

    function_params = get_param_as_python_method_format(docstring_data)
    cmd_line_arguments = get_arguments_from_docstring(docstring_data)
    arguments_as_param = get_arguments_as_param(docstring_data)
    if function_params:
        cells.remove(first_code_cell)
    return DocstringWrapper(docstring_str, function_params,
                            cmd_line_arguments, arguments_as_param)


def filter_no_effect(cell_content: str, resource: dict) -> str:
    """
        Filter cell with no effect statement
    """
    for keyword in resource.get('ignore_keys', [DEFAULT_IGNORE_KEY]):
        if keyword in cell_content:
            logging.warning('Discard cell with no effect')
            return ''
    return cell_content


def is_code_cell(cell: NotebookNode) -> bool:
    return cell.cell_type == 'code'


class IPynbToPython(CommandHelper):

    def run(self, *args, **kwargs):
        args = ArgumentBuilder(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                               description='Convert Notebook to python script') \
            .add_work_dir_argument() \
            .add_conf_path_argument() \
            .add_force_argument() \
            .add_argument('-n', '--notebook', type=str, required=True,
                          help='The notebook to convert') \
            .add_argument('-o', '--output', type=str,
                          help='The Python script output path') \
            .parse(args)
        work_directory = args.working_directory or get_work_directory(args.notebook)
        conf_path = args.conf_path or get_conf_file_default_path(work_directory)
        conf = load_conf_or_default(conf_path, work_directory)

        if not conf.path and not args.output:
            raise MlVToolException('Parameter --output is mandatory if no conf provided')

        output = args.output or get_script_output_path(args.notebook, conf)

        if not args.force and exists(output):
            raise MlVToolException(f'Output file {output} already exists, use --force option to overwrite it')

        export(args.notebook, output, conf)
        logging.info(f'Python script generated in {abspath(output)}')
