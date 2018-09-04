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
