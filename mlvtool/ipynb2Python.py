#!/usr/bin/env python3
import argparse
import logging
from collections import namedtuple
from os import makedirs
from os.path import abspath
from os.path import realpath, dirname, join, basename

import docstring_parser as dc_parser
from nbconvert import PythonExporter

from mlvtool.cmd import CommandHelper
from mlvtool.exception import MlVToolException

logging.getLogger().setLevel(logging.INFO)
CURRENT_DIR = realpath(dirname(__file__))
TEMPLATE_PATH = join(CURRENT_DIR, '..', 'template', 'ml-python.pl')


def get_config(template_path: str) -> dict:
    return {'TemplateExporter': {'template_file': template_path},
            'NbConvertApp': {'export_format': 'python'}}


DocstringWrapper = namedtuple('DocstringWrapper',
                              ('docstring_by_line', 'params'))


def extract_docstring_and_param(cell_content: str) -> DocstringWrapper:
    recording = False
    docstring = []
    # TODO improve docstring extraction
    for line in cell_content.split('\n'):
        nb_occ_separator = line.count('"""')
        if nb_occ_separator:
            # Inline specific case
            if (not recording and docstring) or nb_occ_separator > 2:
                raise MlVToolException(
                    f'Only one docstring allowed in first Notebook cell, '
                    f'{len(docstring)} found')
            if nb_occ_separator == 2:
                docstring.append(line.strip())
                continue
            recording = not recording
            docstring.append(line.strip())
            continue
        if recording:
            docstring.append(line.strip())
    if docstring:
        try:
            docstring_data = dc_parser.parse(
                '\n'.join(docstring).replace('\t', ''))
        except dc_parser.ParseError as e:
            raise MlVToolException(f'Docstring format error. {e}') from e
        if not docstring_data:
            raise MlVToolException('Cannot parse docstring from first cell.')

        params = ['{}{}'.format(p.arg_name,
                                '' if not p.type_name else f':{p.type_name}')
                  for p in docstring_data.params]
        return DocstringWrapper(docstring, ', '.join(params))
    return DocstringWrapper([], '')


def export(input_notebook_path: str, output_path: str):
    exporter = PythonExporter(get_config(TEMPLATE_PATH))
    exporter.register_filter(name='extract_docstring_and_param',
                             jinja_filter=extract_docstring_and_param)
    try:
        output_script, _ = exporter.from_filename(input_notebook_path)
    except Exception as e:
        raise e
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
            script_name = '{}.py'.format(
                basename(args.notebook).replace('.ipynb', '')
                    .replace(' ', '_')
                    .lower())
            output_path = join(CURRENT_DIR, '..', 'pipeline', 'steps',
                               script_name)

        export(args.notebook, output_path)
        logging.info(f'Python script generated in {abspath(output_path)}')


if __name__ == '__main__':
    CommandHelper.run()
