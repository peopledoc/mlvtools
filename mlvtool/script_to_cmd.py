#!/usr/bin/env python3
import argparse
import logging
from os import chmod
from os.path import abspath, relpath, join, exists
from os.path import realpath, dirname
from typing import List

from jinja2 import Environment, FileSystemLoader

from mlvtool.cmd import CommandHelper, ArgumentBuilder
from mlvtool.conf.conf import get_python_cmd_output_path, get_dvc_cmd_output_path, load_conf_or_default, MlVToolConf, \
    get_conf_file_default_path, get_work_directory
from mlvtool.docstring_helpers.extract import extract_docstring_from_file, DocstringInfo
from mlvtool.docstring_helpers.parse import get_dvc_params, DocstringDvc
from mlvtool.exception import MlVToolException
from mlvtool.helper import extract_type, to_cmd_param, to_bash_variable

logging.getLogger().setLevel(logging.INFO)
CURRENT_DIR = realpath(dirname(__file__))
PYTHON_CMD_TEMPLATE_NAME = 'python-cmd.pl'
DVC_CMD_TEMPLATE_NAME = 'dvc-cmd.pl'


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
        type_info = extract_type(param.type_name)
        info['params'].append({'name': to_cmd_param(param.arg_name),
                               'type': type_info.type_name,
                               'help': param.description,
                               'is_list': type_info.is_list})
        arg_params.append(f'args.{param.arg_name}')

    info['arg_params'] = ', '.join(arg_params)
    return info


def get_dvc_template_data(docstring_info: DocstringInfo, python_cmd_path: str):
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


def gen_dvc_command(docstring_info: DocstringInfo, output_path: str, python_script_path: str, conf: MlVToolConf):
    info = get_dvc_template_data(docstring_info, relpath(python_script_path, conf.top_directory))
    write_template(output_path, DVC_CMD_TEMPLATE_NAME, info=info)
    logging.info(f'Dvc bash command successfully generated in {output_path}')


def gen_commands(input_path: str, py_output_path: str, src_dir: str, conf, dvc_output_path: str = None):
    docstring_info = extract_docstring_from_file(input_path)
    gen_python_command(docstring_info, py_output_path, src_dir)
    if dvc_output_path:
        gen_dvc_command(docstring_info, dvc_output_path, py_output_path, conf)


class MlScriptToCmd(CommandHelper):

    def run(self, *args, **kwargs):
        args = ArgumentBuilder(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                               description='Generate python script wrappers') \
            .add_work_dir_argument() \
            .add_conf_path_argument() \
            .add_force_argument() \
            .add_argument('-i', '--input-script', type=str, required=True,
                          help='The python input script') \
            .add_argument('--out-py-cmd', type=str,
                          help='Path to the generated python command') \
            .add_argument('--out-dvc-cmd', type=str,
                          help='Path to the generated bash dvc command') \
            .add_argument('--no-dvc', action='store_true',
                          help='No dvc script generation') \
            .add_argument('--python-src-dir', type=str,
                          help='Python source directory. Default: git root dir.') \
            .parse(args)
        work_directory = args.working_directory or get_work_directory(args.input_script)
        conf_path = args.conf_path or get_conf_file_default_path(work_directory)
        conf = load_conf_or_default(conf_path, work_directory)

        if not conf.path and not args.out_py_cmd:
            raise MlVToolException('Parameter --out-py-cmd is mandatory if no conf provided')
        if not (conf.path or args.out_dvc_cmd or args.no_dvc):
            raise MlVToolException('Parameter --out-dvc-cmd is mandatory if no conf provided')

        out_py_cmd = args.out_py_cmd or get_python_cmd_output_path(args.input_script, conf)
        out_dvc_cmd = args.out_dvc_cmd or (conf.path and get_dvc_cmd_output_path(args.input_script, conf))

        python_src_dir = args.python_src_dir or work_directory
        if not args.force:
            self.check_output(out_py_cmd)
            if not args.no_dvc:
                self.check_output(out_dvc_cmd)

        gen_commands(args.input_script, out_py_cmd, python_src_dir, conf,
                     dvc_output_path=None if args.no_dvc else out_dvc_cmd)

    def check_output(self, path):
        if exists(path):
            raise MlVToolException(f'Output file {path} already exists, use --force'
                                   f' option to overwrite it.')
