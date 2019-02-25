import stat
from collections import namedtuple
from os import stat as os_stat
from os.path import join, exists

from mlvtools.conf.conf import DEFAULT_CONF_FILENAME
from mlvtools.ipynb_to_python import IPynbToPython
from tests.helpers.utils import gen_notebook, write_conf


def is_in(expected: str, file_content: str):
    sanitized_expected = expected.replace('\n', '').replace(' ', '')
    sanitized_file_content = file_content.replace('\n', '').replace(' ', '')

    return sanitized_expected in sanitized_file_content


KeptCells = namedtuple('KeptCells', ('code', 'comment'))
DroppedCells = namedtuple('DroppedCells', ('no_effect', 'docstring_cell'))


def generate_test_notebook(work_dir: str, notebook_name: str):
    docstring = '"""\n' \
                ':param str subset: The kind of subset to generate.\n' \
                ':param int rate:\n' \
                ':dvc-out output_file: {{ conf.output_file }}\n' \
                '"""\n'
    docstring_cell = ('code', '#Parameters\n{}subset = "train"\n'.format(docstring))
    code_cells = [
        ('code',
         'import numpy as np\n'
         'import pandas as pd\n'
         'from sklearn.datasets import fetch_20newsgroups\n'),
        ('code',
         'newsgroups_train = fetch_20newsgroups(subset=subset,\n'
         '            remove=("headers", "footers", "quotes"))'),
        ('code', 'df_train.to_csv("data_train.csv", index=None)')
    ]
    comment_cell = ('markdown', 'This is a comment cell')
    no_effect_cells = [('code', '# Ignore\n# No effect'
                                'df_train = pd.DataFrame(newsgroups_train.data, columns=["data"])'),
                       ('code', '# No effect\ndf_train')]

    cells = [
        docstring_cell,
        code_cells[0],
        code_cells[1],
        comment_cell,
        no_effect_cells[0],
        no_effect_cells[1],
        code_cells[2]
    ]

    notebook_path = gen_notebook(cells, work_dir, notebook_name)
    dropped_cells = DroppedCells(no_effect_cells, docstring_cell)
    kept_cells = KeptCells(code_cells, [comment_cell])
    return kept_cells, dropped_cells, docstring, notebook_path


def check_content(docstring: str, kept_cells: KeptCells, dropped_cells: DroppedCells, file_content):
    assert is_in(docstring, file_content), 'Docstring not found in generated script'

    for _, cell in kept_cells.code:
        assert is_in(cell, file_content), f'Code cell {cell} not found in generated script'
    for _, cell in kept_cells.comment:
        assert is_in(cell, file_content), f'Comment cell {cell} not found in generated script'

    for _, cell in dropped_cells.no_effect:
        assert not is_in(cell, file_content), f'No effect cell {cell} must be dropped'
    assert not is_in(dropped_cells.docstring_cell[1], file_content), f'Docstring cell {cell} must be dropped'


def test_should_generate_python_script_no_conf(work_dir):
    """
        Convert a Jupyter Notebook to a Python 3 script using all parameters
        - create right function name
        - keep the docstring
        - keep code cells
        - remove no effect cells
        - remove trailing cells
        - call the function with right arguments
        - python syntax is ok
        - the script is executable
    """
    kept_cells, dropped_cells, docstring, notebook_path = generate_test_notebook(work_dir=work_dir,
                                                                                 notebook_name='test_nb.ipynb')

    output_path = join(work_dir, 'out.py')
    cmd_arguments = ['-n', notebook_path, '-o', output_path, '--working-directory', work_dir]
    IPynbToPython().run(*cmd_arguments)

    assert exists(output_path)

    with open(output_path, 'r') as fd:
        file_content = fd.read()

    check_content(docstring, kept_cells, dropped_cells, file_content)
    assert 'def mlvtools_test_nb(subset: str, rate: int):' in file_content
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
    kept_cells, dropped_cells, docstring, notebook_path = generate_test_notebook(work_dir=work_dir,
                                                                                 notebook_name='test_nb.ipynb')
    # Create conf with knew ignore cell keywords
    conf_data = write_conf(work_dir=work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME),
                           ignore_keys=['# Ignore', 'import'])

    cmd_arguments = ['-n', notebook_path]
    IPynbToPython().run(*cmd_arguments)

    # This path is generated using the conf script_dir and the notebook name
    output_script_path = join(work_dir, conf_data['path']['python_script_root_dir'], 'mlvtools_test_nb.py')
    assert exists(output_script_path)

    with open(output_script_path, 'r') as fd:
        file_content = fd.read()

    # With those knew keywords from conf the first code cell must be ignored (due to import)
    # The second no effect cell must remain because "# No effect" is no more a keyword
    assert not is_in(kept_cells.code[0][1], file_content)
    assert is_in(dropped_cells.no_effect[1][1], file_content)

    # Check conf file has been found using git rev-parse command
    assert mocked_check_output.mock_calls == [mocker.call(
        ['git', 'rev-parse', '--show-toplevel'],
        cwd=work_dir)]
