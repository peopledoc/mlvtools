import subprocess
import tempfile
from os.path import join, exists

from mlvtool.conf.conf import DEFAULT_CONF_FILENAME
from mlvtool.ipynb_to_python import IPynbToPython
from tests.helpers.utils import gen_notebook, write_conf


def is_in(expected: str, file_content: str):
    sanitized_expected = expected.replace('\n', '').replace(' ', '')
    sanitized_file_content = file_content.replace('\n', '').replace(' ', '')

    return sanitized_expected in sanitized_file_content


def generate_test_notebook(work_dir: str, notebook_name: str):
    docstring = '"""\n' \
                ':param str subset: The kind of subset to generate.\n' \
                ':param int rate:\n' \
                '"""\n'
    cells = [

        '#Parameters\n{}subset = "train"\n'.format(docstring),

        'import numpy as np\n'
        'import pandas as pd\n'
        'from sklearn.datasets import fetch_20newsgroups\n',

        'newsgroups_train = fetch_20newsgroups(subset=subset,\n'
        '            remove=("headers", "footers", "quotes"))',

        '# Ignore\n'
        'df_train = pd.DataFrame(newsgroups_train.data, columns=["data"])',

        '# No effect\n'
        'df_train',

        'df_train.to_csv("data_train.csv", index=None)'
    ]
    notebook_path = gen_notebook(cells, work_dir, notebook_name)
    return cells, docstring, notebook_path


def test_should_generate_python_script_no_conf():
    """
        Convert a Jupyter Notebook to a Python 3 script using all parameters
    """
    with tempfile.TemporaryDirectory() as tmp:
        cells, docstring, notebook_path = generate_test_notebook(work_dir=tmp,
                                                                 notebook_name='test_nb.ipynb')

        output_path = join(tmp, 'out.py')
        cmd_arguments = ['-n', notebook_path, '-o', output_path, '--working-directory', tmp]
        IPynbToPython().run(*cmd_arguments)

        assert exists(output_path)

        with open(output_path, 'r') as fd:
            file_content = fd.read()

        assert 'def test_nb(subset: str, rate: int):' in file_content
        assert is_in(docstring, file_content)
        assert not is_in(cells[0], file_content)
        assert is_in(cells[1], file_content)
        assert is_in(cells[2], file_content)
        assert is_in(cells[3], file_content)
        assert not is_in(cells[4], file_content)
        assert is_in(cells[5], file_content)

        # Ensure generated file syntax is right
        compile(file_content, output_path, 'exec')


def test_should_generate_python_script_with_conf_auto_detect():
    """
        Convert a Jupyter Notebook to a Python 3 script using conf
    """
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.check_output(['git', 'init'], cwd=tmp)
        cells, docstring, notebook_path = generate_test_notebook(work_dir=tmp,
                                                                 notebook_name='test_nb.ipynb')
        # Create conf in a freshly init git repo
        conf_data = write_conf(work_dir=tmp, conf_path=join(tmp, DEFAULT_CONF_FILENAME),
                               ignore_keys=['# Ignore', 'remove='])

        cmd_arguments = ['-n', notebook_path]
        IPynbToPython().run(*cmd_arguments)

        # This path is generated using the conf script_dir and the notebook name
        output_script_path = join(tmp, conf_data['path']['python_script_root_dir'], 'test_nb.py')
        assert exists(output_script_path)

        with open(output_script_path, 'r') as fd:
            file_content = fd.read()

        assert 'def test_nb(subset: str, rate: int):' in file_content
        assert is_in(docstring, file_content)
        assert not is_in(cells[0], file_content)
        assert is_in(cells[1], file_content)
        assert not is_in(cells[2], file_content)
        assert not is_in(cells[3], file_content)
        assert is_in(cells[4], file_content)
        assert is_in(cells[5], file_content)

        # Ensure generated file syntax is right
        compile(file_content, output_script_path, 'exec')
