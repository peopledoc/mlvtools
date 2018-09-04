import tempfile
from os.path import join, exists

from mlvtool.ipynb_to_python import export
from tests.helpers.utils import gen_notebook


def is_in(expected: str, file_content: str):
    sanitized_expected = expected.replace('\n', '').replace(' ', '')
    sanitized_file_content = file_content.replace('\n', '').replace(' ', '')

    return sanitized_expected in sanitized_file_content


def test_should_generate_python_script():
    with tempfile.TemporaryDirectory() as tmp:
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

            'df_train = pd.DataFrame(newsgroups_train.data, columns=["data"])',

            '# No effect\n'
            'df_train',

            'df_train.to_csv("data_train.csv", index=None)'
        ]

        notebook_path = gen_notebook(cells, tmp, 'test_nb.ipynb')

        output_path = join(tmp, 'out.py')
        export(notebook_path, output_path)

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
