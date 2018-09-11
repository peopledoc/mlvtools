import json
from os import makedirs
from os.path import join
from typing import List

import nbformat as nbf


def gen_notebook(cells: List[str], tmp_dir: str, file_name: str,
                 docstring: str = None, header: str = None):
    nb = nbf.v4.new_notebook()
    if header:
        nb['cells'].append(nbf.v4.new_markdown_cell(header))
    if docstring:
        nb['cells'].append(nbf.v4.new_code_cell(docstring))
    for cell_content in cells:
        nb['cells'].append(nbf.v4.new_code_cell(cell_content))
    notebook_path = join(tmp_dir, file_name)
    nbf.write(nb, notebook_path)
    return notebook_path


def write_conf(work_dir: str, conf_path: str, ignore_keys: List[str] = None,
               script_dir: str = None, py_cmd_dir: str = None,
               dvc_cmd_dir: str = None, dvc_py_cmd_path: str = None,
               dvc_py_cmd_name: str = None) -> dict:
    ignore_keys = ignore_keys or []
    script_dir = script_dir or join('script')
    py_cmd_dir = py_cmd_dir or join('cmd', 'py')
    dvc_cmd_dir = dvc_cmd_dir or join('cmd', 'dvc')
    makedirs(join(work_dir, script_dir))
    makedirs(join(work_dir, py_cmd_dir))
    makedirs(join(work_dir, dvc_cmd_dir))
    conf_data = {
        'path': {
            'python_script_root_dir': script_dir,
            'python_cmd_root_dir': py_cmd_dir,
            'dvc_cmd_root_dir': dvc_cmd_dir
        },
        'ignore_keys': ignore_keys,
    }
    if dvc_py_cmd_name:
        conf_data['dvc_var_python_cmd_name'] = dvc_py_cmd_name
    if dvc_py_cmd_path:
        conf_data['dvc_var_python_cmd_path'] = dvc_py_cmd_path
    with open(conf_path, 'w') as fd:
        json.dump(conf_data, fd)
    return conf_data


def write_min_script(script_path: str):
    python_script = 'def my_funct():\n' \
                    '\t""" A description """\n' \
                    '\tpass\n'
    with open(script_path, 'w') as fd:
        fd.write(python_script)
