#!/usr/bin/env python3
import argparse
import logging
from collections import namedtuple
from os import makedirs
from os.path import abspath
from os.path import realpath, dirname, join, basename
from typing import List

import docstring_parser as dc_parser
from nbconvert import PythonExporter

from mlvtool.cmd import CommandHelper
from mlvtool.exception import MlVToolException

NO_EFFECT_STATEMENT = '#No effect'

logging.getLogger().setLevel(logging.INFO)
CURRENT_DIR = realpath(dirname(__file__))
TEMPLATE_PATH = join(CURRENT_DIR, '..', 'template', 'ml-python.pl')

DocstringWrapper = namedtuple('DocstringWrapper',
                              ('docstring_by_line', 'params'))


def get_config(template_path: str) -> dict:
    return {'TemplateExporter': {'template_file': template_path},
            'NbConvertApp': {'export_format': 'python'}}


def extract_docstring(cell_content: str) -> List[str]:
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


def extract_param_str(docstring_str: str) -> str:
    if not docstring_str:
        return ''
    try:
        docstring_data = dc_parser.parse(docstring_str.replace('\t', ''))
    except dc_parser.ParseError as e:
        raise MlVToolException(f'Docstring format error. {e}') from e
    if not docstring_data:
        raise MlVToolException('Cannot parse docstring from first cell.')

    params = ['{}{}'.format(p.arg_name,
                            '' if not p.type_name else f':{p.type_name}')
              for p in docstring_data.params]
    return ', '.join(params)


def extract_docstring_and_param(cell_content: str) -> DocstringWrapper:
    docstrings = extract_docstring(cell_content)
    params = extract_param_str('\n'.join(docstrings))
    return DocstringWrapper(docstrings, params)


def filter_no_effect(cell_content: str) -> str:
    if NO_EFFECT_STATEMENT in cell_content:
        logging.warning('Discard cell with no effect')
        return ''
    return cell_content


def export(input_notebook_path: str, output_path: str):
    exporter = PythonExporter(get_config(TEMPLATE_PATH))
    exporter.register_filter(name='extract_docstring_and_param',
                             jinja_filter=extract_docstring_and_param)
    exporter.register_filter(name='filter_no_effect',
                             jinja_filter=filter_no_effect)
    try:
        output_script, _ = exporter.from_filename(input_notebook_path)
    except Exception as e:
        raise MlVToolException(e) from e

    if not output_script:
        logging.warning('Empty notebook provided. Nothing to do.')
        return
    makedirs(dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as fd:
        fd.write(output_script)


class IPynbToPython(CommandHelper):

    def run(self, *args, **kwargs):
        parser = argparse.ArgumentParser(
            description='Convert Notebook to python '
                        'script')
        parser.add_argument('-n', '--notebook', type=str, required=True,
                            help='The notebook to convert')
        parser.add_argument('-o', '--output', type=str,
                            help='The Python script output path')
        args = parser.parse_args()

        output_path = args.output
        if not output_path:
            script_name = '{}.py'.format(basename(args.notebook)
                                         .replace('.ipynb', '')
                                         .replace(' ', '_')
                                         .lower())
            output_path = join(CURRENT_DIR, '..', 'pipeline', 'steps',
                               script_name)

        export(args.notebook, output_path)
        logging.info(f'Python script generated in {abspath(output_path)}')


if __name__ == '__main__':
    CommandHelper.run()
