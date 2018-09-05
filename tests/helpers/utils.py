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


def write_conf(work_dir: str, conf_path: str, ignore_keys: List[str],
               script_dir: str = None, py_cmd_dir: str = None,
               dvc_cmd_dir: str = None) -> dict:
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
    with open(conf_path, 'w') as fd:
        json.dump(conf_data, fd)
    return conf_data
