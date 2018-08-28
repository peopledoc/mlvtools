#!/usr/bin/env python3
import argparse
import ast
import logging
import subprocess
from collections import namedtuple
from os import chmod
from os.path import abspath, relpath, join, exists
from os.path import realpath, dirname

from docstring_parser import parse as dc_parse
from jinja2 import Environment, FileSystemLoader

from mlvtool.cmd import CommandHelper
from mlvtool.exception import MlVToolException

logging.getLogger().setLevel(logging.INFO)
CURRENT_DIR = realpath(dirname(__file__))
TEMPLATE_NAME = 'python-cmd.pl'


def get_git_top_dir(cwd: str = None) -> str:
    try:
        return subprocess.check_output(['git', 'rev-parse', '--show-toplevel'],
                                       cwd=cwd) \
            .decode() \
            .strip('\n')
    except subprocess.SubprocessError as e:
        message = 'Can not run \'git rev-parse\' command to get top directory.'
        logging.fatal(message)
        raise MlVToolException(message) from e


def get_import_line(file_path: str, prj_src_dir: str, method_name: str) -> str:
    module_path = relpath(abspath(file_path), abspath(prj_src_dir))
    if module_path.startswith('..'):
        raise Exception(f'Wrong source dir provided {prj_src_dir}')

    modules = module_path.replace('/', '.').replace('.py', '')
    return f'from {modules} import {method_name}'


DocstringInfo = namedtuple('DocstringInfo',
                           ('method_name', 'docstring', 'repr', 'file_path'))


def extract_docstring(input_path: str) -> DocstringInfo:
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


def get_info(docstring_info: DocstringInfo, src_dir: str) -> dict:
    if not docstring_info.docstring:
        logging.warning('No docstring found.')

    if not docstring_info.docstring.params:
        logging.warning('No params found.')

    info = {'params': [], 'method_name': docstring_info.method_name,
            'import_line': get_import_line(docstring_info.file_path, src_dir,
                                           docstring_info.method_name)}
    arg_params = []
    for param in docstring_info.docstring.params:
        info['params'].append({'name': param.arg_name.replace('_', '-'),
                               'type': param.type_name,
                               'help': param.description})
        arg_params.append(f'args.{param.arg_name}')

    info['arg_params'] = ', '.join(arg_params)

    return info


def gen_python_script(input_path: str, output_path: str, src_dir: str,
                      template_name: str):
    docstring_info = extract_docstring(input_path)
    info = get_info(docstring_info, src_dir)
    loader = FileSystemLoader(searchpath=join(CURRENT_DIR, '..', 'template'))
    jinja_env = Environment(loader=loader)
    content = jinja_env.get_template(template_name) \
        .render(info=info, docstring=f'"""\n{docstring_info.repr}\n"""')
    with open(output_path, 'w') as fd:
        fd.write(content)
    chmod(output_path, 0o755)
    logging.info(f'Python command successfully generated in {output_path}')


class MlScriptToCmd(CommandHelper):
    def run(self, *args, **kwargs):
        parser = argparse.ArgumentParser(description='Generate python script '
                                                     'wrappers')
        parser.add_argument('-i', '--input-script', type=str, required=True,
                            help='The python input script')
        parser.add_argument('--out-py-cmd', type=str, required=True,
                            help='Path to the generated python command')
        parser.add_argument('--out-bash-cmd', type=str, required=True,
                            help='Path to the generated bash command')
        parser.add_argument('--python-src-dir', type=str,
                            default=get_git_top_dir(),
                            help='Python source directory. '
                                 'Default: git root dir.')
        parser.add_argument('-f', '--force', action='store_true',
                            help='Force output overwrite.')
        args = parser.parse_args()

        if not args.force:
            for path in (args.out_py_cmd, args.out_bash_cmd):
                if exists(path):
                    logging.error(
                        f'Output file {path} already exists, use --force'
                        f' option to overwrite it.')
                    exit(1)
        gen_python_script(args.input_script, args.out_py_cmd,
                          args.python_src_dir,
                          TEMPLATE_NAME)


if __name__ == '__main__':
    MlScriptToCmd().run()
