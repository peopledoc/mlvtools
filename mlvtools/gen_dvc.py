#!/usr/bin/env python3
import argparse
import logging
from os.path import realpath, dirname
from os.path import relpath, join, exists, basename
from typing import List

from mlvtools.cmd import CommandHelper, ArgumentBuilder
from mlvtools.conf.conf import get_dvc_cmd_output_path, load_conf_or_default, get_conf_file_default_path, \
    get_work_directory, load_docstring_conf, MlVToolConf
from mlvtools.docstring_helpers.extract import extract_docstring_from_file, DocstringInfo
from mlvtools.docstring_helpers.parse import get_dvc_params, DocstringDvc
from mlvtools.exception import MlVToolException
from mlvtools.helper import to_cmd_param, to_bash_variable, to_dvc_meta_filename, write_template

logging.getLogger().setLevel(logging.INFO)
CURRENT_DIR = realpath(dirname(__file__))
DVC_CMD_TEMPLATE_NAME = 'dvc-cmd.tpl'


def get_dvc_template_data(docstring_info: DocstringInfo, python_cmd_path: str, meta_file_variable_name: str,
                          extra_variables: dict = None):
    """
        Format data from docstring for dvc bash command template
    """
    dvc_params = get_dvc_params(docstring_info.docstring)
    variables = [] if not extra_variables else [f'{name}="{value}"' for name, value in extra_variables.items()]
    meta_file_name = dvc_params.meta_file_name or to_dvc_meta_filename(python_cmd_path)

    info = {
        'variables': variables,
        'meta_file_name_var_assign': f'{meta_file_variable_name}="{meta_file_name}"',
        'meta_file_name_var': meta_file_variable_name
    }

    if dvc_params.dvc_cmd:
        info['whole_command'] = dvc_params.dvc_cmd.cmd.replace('\n', ' \\\n')
        return info
    # keep meta file name default value if not specified
    info['python_script'] = python_cmd_path
    info['dvc_inputs'] = []
    info['dvc_outputs'] = []
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


def gen_command(input_path: str, dvc_output_path: str, conf: MlVToolConf, docstring_conf: dict = None):
    docstring_info = extract_docstring_from_file(input_path, docstring_conf)
    python_cmd_rel_path = relpath(input_path, conf.top_directory)

    extra_var = {conf.dvc_var_python_cmd_path: python_cmd_rel_path,
                 conf.dvc_var_python_cmd_name: basename(python_cmd_rel_path)}
    info = get_dvc_template_data(docstring_info, python_cmd_rel_path, conf.dvc_var_meta_filename, extra_var)

    template_path = join(CURRENT_DIR, '..', 'template', DVC_CMD_TEMPLATE_NAME)
    write_template(dvc_output_path, template_path, info=info)
    logging.info(f'Dvc bash command successfully generated in {dvc_output_path}')


class MlScriptToCmd(CommandHelper):

    def run(self, *args, **kwargs):
        args = ArgumentBuilder(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                               description='Generate python script wrappers') \
            .add_work_dir_argument() \
            .add_conf_path_argument() \
            .add_force_argument() \
            .add_docstring_conf() \
            .add_argument('-i', '--input-script', type=str, required=True,
                          help='The python input script') \
            .add_argument('-o', '--out-dvc-cmd', type=str,
                          help='Path to the generated bash dvc command') \
            .parse(args)

        work_directory = args.working_directory or get_work_directory(args.input_script)
        conf_path = args.conf_path or get_conf_file_default_path(work_directory)
        conf = load_conf_or_default(conf_path, work_directory)
        docstring_conf_path = args.docstring_conf or conf.docstring_conf

        if not conf.path and not args.out_dvc_cmd:
            raise MlVToolException('Parameter --out-dvc-cmd is mandatory if no conf provided')

        docstring_conf = load_docstring_conf(docstring_conf_path) if docstring_conf_path else None
        out_dvc_cmd = args.out_dvc_cmd or get_dvc_cmd_output_path(args.input_script, conf)

        if not args.force:
            self.check_output(out_dvc_cmd)

        gen_command(args.input_script, out_dvc_cmd, conf, docstring_conf)

    def check_output(self, path):
        if exists(path):
            raise MlVToolException(f'Output file {path} already exists, use --force'
                                   f' option to overwrite it.')
