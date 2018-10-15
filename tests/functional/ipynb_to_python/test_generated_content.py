import stat
from os import stat as os_stat
from os.path import join, exists

from mlvtools.conf.conf import DEFAULT_CONF_FILENAME
from mlvtools.ipynb_to_python import IPynbToPython
from tests.helpers.utils import gen_notebook, write_conf


def is_in(expected: str, file_content: str):
    sanitized_expected = expected.replace('\n', '').replace(' ', '')
    sanitized_file_content = file_content.replace('\n', '').replace(' ', '')

    return sanitized_expected in sanitized_file_content


def generate_test_notebook(work_dir: str, notebook_name: str):
    docstring = '"""\n' \
                ':param str subset: The kind of subset to generate.\n' \
                ':param int rate:\n' \
                ':dvc-out output_file: {{ conf.output_file }}\n' \
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


def test_should_generate_python_script_no_conf(work_dir):
    """
        Convert a Jupyter Notebook to a Python 3 script using all parameters
    """
    cells, docstring, notebook_path = generate_test_notebook(work_dir=work_dir,
                                                             notebook_name='test_nb.ipynb')

    output_path = join(work_dir, 'out.py')
    cmd_arguments = ['-n', notebook_path, '-o', output_path, '--working-directory', work_dir]
    IPynbToPython().run(*cmd_arguments)

    assert exists(output_path)

    with open(output_path, 'r') as fd:
        file_content = fd.read()

    assert 'def mlvtools_test_nb(subset: str, rate: int):' in file_content
    assert is_in(docstring, file_content)
    assert not is_in(cells[0], file_content)
    assert is_in(cells[1], file_content)
    assert is_in(cells[2], file_content)
    assert is_in(cells[3], file_content)
    assert not is_in(cells[4], file_content)
    assert is_in(cells[5], file_content)
    assert 'mlvtools_test_nb(args.subset, args.rate)' in file_content

    # Ensure generated file syntax is right
    compile(file_content, output_path, 'exec')
    # Ensure script has exe right
    assert stat.S_IMODE(os_stat(output_path).st_mode) == 0o755


def test_should_generate_python_script_with_conf_auto_detect(work_dir, mocker):
    """
        Convert a Jupyter Notebook to a Python 3 script using conf
    """
    mocked_check_output = mocker.patch('subprocess.check_output', return_value=work_dir.encode())
    cells, docstring, notebook_path = generate_test_notebook(work_dir=work_dir,
                                                             notebook_name='test_nb.ipynb')
    # Create conf in a freshly init git repo
    conf_data = write_conf(work_dir=work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME),
                           ignore_keys=['# Ignore', 'remove='])

    cmd_arguments = ['-n', notebook_path]
    IPynbToPython().run(*cmd_arguments)

    # This path is generated using the conf script_dir and the notebook name
    output_script_path = join(work_dir, conf_data['path']['python_script_root_dir'], 'mlvtools_test_nb.py')
    assert exists(output_script_path)

    with open(output_script_path, 'r') as fd:
        file_content = fd.read()

    assert 'def mlvtools_test_nb(subset: str, rate: int):' in file_content
    assert is_in(docstring, file_content)
    assert not is_in(cells[0], file_content)
    assert is_in(cells[1], file_content)
    assert not is_in(cells[2], file_content)
    assert not is_in(cells[3], file_content)
    assert is_in(cells[4], file_content)
    assert is_in(cells[5], file_content)

    # Ensure generated file syntax is right
    compile(file_content, output_script_path, 'exec')

    assert mocked_check_output.mock_calls == [mocker.call(
        ['git', 'rev-parse', '--show-toplevel'],
        cwd=work_dir)]
