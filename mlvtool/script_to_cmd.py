#!/usr/bin/env python3
import argparse
import logging
import subprocess
from os import chmod
from os.path import abspath, relpath, join, exists
from os.path import realpath, dirname
from typing import List

from jinja2 import Environment, FileSystemLoader

from mlvtool.cmd import CommandHelper
from mlvtool.docstring_helpers.extract import extract_docstring_from_file, DocstringInfo
from mlvtool.docstring_helpers.parse import get_dvc_params, DocstringDvc
from mlvtool.exception import MlVToolException
from mlvtool.helper import to_cmd_param, to_bash_variable

logging.getLogger().setLevel(logging.INFO)
CURRENT_DIR = realpath(dirname(__file__))
PYTHON_CMD_TEMPLATE_NAME = 'python-cmd.pl'
DVC_CMD_TEMPLATE_NAME = 'dvc-cmd.pl'


def get_git_top_dir(cwd: str = None) -> str:
    try:
        return subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=cwd) \
            .decode() \
            .strip('\n')
    except subprocess.SubprocessError as e:
        message = 'Can not run \'git rev-parse\' command to get top directory.'
        logging.fatal(message)
        raise MlVToolException(message) from e


def get_import_line(file_path: str, prj_src_dir: str, method_name: str) -> str:
    """
        Deduce python script import line from project source directory path
    """
    module_path = relpath(abspath(file_path), abspath(prj_src_dir))
    if module_path.startswith('..'):
        raise Exception(f'Wrong source dir provided {prj_src_dir}')

    modules = module_path.replace('/', '.').replace('.py', '')
    return f'from {modules} import {method_name}'


def get_py_template_data(docstring_info: DocstringInfo, src_dir: str) -> dict:
    """
        Format data from docstring for python command template
    """
    if not docstring_info.docstring:
        logging.warning('No docstring found.')

    if not docstring_info.docstring.params:
        logging.warning('No params found.')

    info = {'params': [],
            'method_name': docstring_info.method_name,
            'import_line': get_import_line(docstring_info.file_path, src_dir,
                                           docstring_info.method_name)}
    arg_params = []
    for param in docstring_info.docstring.params:
        info['params'].append({'name': to_cmd_param(param.arg_name),
                               'type': param.type_name,
                               'help': param.description})
        arg_params.append(f'args.{param.arg_name}')

    info['arg_params'] = ', '.join(arg_params)
    return info


def get_bash_template_data(docstring_info: DocstringInfo, python_cmd_path: str):
    """
        Format data from docstring for dvc bash command template
    """
    dvc_params = get_dvc_params(docstring_info.docstring)
    if dvc_params.dvc_cmd:
        return {'whole_command': dvc_params.dvc_cmd.cmd.replace('\n', ' \\\n')}

    info = {'python_script': python_cmd_path,
            'dvc_inputs': [],
            'dvc_outputs': [],
            'variables': []}
    python_params = []

    def handle_params(dvc_docstring_params: List[DocstringDvc], label: str):
        for dvc_param in dvc_docstring_params:
            if dvc_param.related_param:
                variable_name = to_bash_variable(dvc_param.related_param)
                py_cmd_param = to_cmd_param(dvc_param.related_param)
                info['variables'].append(f'{variable_name}="{dvc_param.file_path}"')
                python_params.append(f'--{py_cmd_param} ${variable_name}')
                info[label].append(f'${variable_name}')
            else:
                info[label].append(dvc_param.file_path)

    for extra_param in dvc_params.dvc_extra:
        python_params.append(extra_param.extra)

    handle_params(dvc_params.dvc_in, 'dvc_inputs')
    handle_params(dvc_params.dvc_out, 'dvc_outputs')
    info['python_params'] = ' '.join(python_params)
    return info


def write_template(output_path, template_name: str, **kwargs):
    loader = FileSystemLoader(searchpath=join(CURRENT_DIR, '..', 'template'))
    jinja_env = Environment(loader=loader)
    content = jinja_env.get_template(template_name) \
        .render(**kwargs)
    with open(output_path, 'w') as fd:
        fd.write(content)
    chmod(output_path, 0o755)


def gen_python_command(docstring_info: DocstringInfo, output_path: str, src_dir: str):
    info = get_py_template_data(docstring_info, src_dir)
    write_template(output_path, PYTHON_CMD_TEMPLATE_NAME, info=info, docstring=f'"""\n{docstring_info.repr}\n"""')
    logging.info(f'Python command successfully generated in {output_path}')


def gen_bash_command(docstring_info: DocstringInfo, output_path: str, python_script_path: str):
    info = get_bash_template_data(docstring_info, relpath(output_path, python_script_path))
    write_template(output_path, DVC_CMD_TEMPLATE_NAME, info=info)
    logging.info(f'Dvc bash command successfully generated in {output_path}')


def gen_commands(input_path: str, py_output_path: str, src_dir: str, bash_output_path: str = None):
    docstring_info = extract_docstring_from_file(input_path)
    gen_python_command(docstring_info, py_output_path, src_dir)
    if bash_output_path:
        gen_bash_command(docstring_info, bash_output_path, py_output_path)


class MlScriptToCmd(CommandHelper):
    def run(self, *args, **kwargs):
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                         description='Generate python script wrappers')
        parser.add_argument('-i', '--input-script', type=str, required=True,
                            help='The python input script')
        parser.add_argument('--out-py-cmd', type=str, required=True,
                            help='Path to the generated python command')
        parser.add_argument('--out-bash-cmd', type=str,
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
        gen_commands(args.input_script, args.out_py_cmd, args.python_src_dir, args.out_bash_cmd)


if __name__ == '__main__':
    MlScriptToCmd().run()
