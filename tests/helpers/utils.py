import json
from os import makedirs
from os.path import join
from typing import List

import nbformat as nbf
import yaml


def gen_notebook(cells: List[str], tmp_dir: str, file_name: str,
                 docstring: str = None, header: str = None):
    nb = nbf.v4.new_notebook()
    if header:
        nb['cells'].append(nbf.v4.new_markdown_cell(header))
    if docstring:
        nb['cells'].append(nbf.v4.new_code_cell(docstring))
    for cell_content in cells:
        nb['cells'].append(to_notebook_code_cell(cell_content))
    notebook_path = join(tmp_dir, file_name)
    nbf.write(nb, notebook_path)
    return notebook_path


def to_notebook_code_cell(cell_content: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(cell_content)


def write_conf(work_dir: str, conf_path: str, ignore_keys: List[str] = None,
               script_dir: str = None, dvc_cmd_dir: str = None,
               dvc_py_cmd_path: str = None, dvc_py_cmd_name: str = None,
               dvc_meta_file_name: str = None, docstring_conf: str = None) -> dict:
    ignore_keys = ignore_keys or []
    script_dir = script_dir or join('script')
    dvc_cmd_dir = dvc_cmd_dir or join('cmd', 'dvc')
    makedirs(join(work_dir, script_dir))
    makedirs(join(work_dir, dvc_cmd_dir))
    conf_data = {
        'path': {
            'python_script_root_dir': script_dir,
            'dvc_cmd_root_dir': dvc_cmd_dir
        },
        'ignore_keys': ignore_keys,
    }
    if dvc_py_cmd_name:
        conf_data['dvc_var_python_cmd_name'] = dvc_py_cmd_name
    if dvc_py_cmd_path:
        conf_data['dvc_var_python_cmd_path'] = dvc_py_cmd_path
    if dvc_meta_file_name:
        conf_data['dvc_var_meta_filename'] = dvc_meta_file_name
    if docstring_conf:
        conf_data['docstring_conf'] = docstring_conf
    with open(conf_path, 'w') as fd:
        json.dump(conf_data, fd)
    return conf_data


def write_min_script(script_path: str, docstring: str = None):
    docstring = docstring or '""" A description """'
    python_script = 'def my_funct():\n' \
                    f'\t{docstring}\n' \
                    '\tpass\n'
    with open(script_path, 'w') as fd:
        fd.write(python_script)


def write_dvc_file(path: str, cmd: str, deps: List[str], outs: List[str]):
    data = {'cmd': cmd,
            'deps': [{'path': dep} for dep in deps],
            'outs': [{'path': out} for out in outs]}
    with open(path, 'w') as fd:
        yaml.dump(data, fd)
