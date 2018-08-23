import tempfile
from os.path import realpath, dirname, join, exists

import nbformat as nbf
import pytest

from mlvtool.exception import MlVToolException
from mlvtool.ipynb2Python import export, extract_docstring_and_param

CURRENT_DIR = realpath(dirname(__file__))


def gen_notebook(nb_cells: int, tmp_dir: str, file_name: str,
                 docstring: str = None):
    nb = nbf.v4.new_notebook()
    if docstring:
        nb['cells'].append(nbf.v4.new_code_cell(docstring))
    for i in range(nb_cells):
        nb['cells'].append(nbf.v4.new_code_cell('print(\'poney\')'))
    notebook_path = join(tmp_dir, file_name)
    nbf.write(nb, notebook_path)
    return notebook_path


def test_should_convert_notebook_to_python_script():
    with tempfile.TemporaryDirectory() as tmp:
        output_path = join(tmp, 'out.py')
        notebook_path = gen_notebook(nb_cells=1, tmp_dir=tmp,
                                     file_name='test.ipynb', docstring=None)
        export(input_notebook_path=notebook_path, output_path=output_path)

        assert exists(output_path)
        with open(output_path, 'r') as fd:
            content = fd.read()

        # Check main method is created
        assert 'def test():' in content


def test_should_detect_parameters():
    with tempfile.TemporaryDirectory() as tmp:
        output_path = join(tmp, 'out.py')

        docstring_cell = '''
        # Parameters
        """
            :param str subset: The kind of subset to generate.
            :param int rate: The rate of I don't know what 
            :param param3:
        """
        subset = 'train'
        toto = 12
        '''

        notebook_path = gen_notebook(nb_cells=1, tmp_dir=tmp,
                                     file_name='test.ipynb',
                                     docstring=docstring_cell)
        export(input_notebook_path=notebook_path, output_path=output_path)
        assert exists(output_path)
        with open(output_path, 'r') as fd:
            content = fd.read()

        # Check main method is created
        assert 'def test(subset:str, rate:int, param3):' in content


def test_should_raise_if_invalid_docstring():
    with tempfile.TemporaryDirectory() as tmp:
        output_path = join(tmp, 'out.py')

        docstring_cell = '''
        # Parameters
        """
            :param param3
        """
        subset = 'train'
        toto = 12
        '''

        notebook_path = gen_notebook(nb_cells=1, tmp_dir=tmp,
                                     file_name='test.ipynb',
                                     docstring=docstring_cell)
        with pytest.raises(Exception):
            export(input_notebook_path=notebook_path, output_path=output_path)


def test_should_raise_if_more_than_one_docstring_in_first_cell():
    with tempfile.TemporaryDirectory() as tmp:
        output_path = join(tmp, 'out.py')

        docstring_cell = '''
        # Parameters
        """
            :param param3: Plop
        """
         """
            :param param6: AA
        """
        subset = 'train'
        toto = 12
        '''

        notebook_path = gen_notebook(nb_cells=1, tmp_dir=tmp,
                                     file_name='test.ipynb',
                                     docstring=docstring_cell)
        with pytest.raises(Exception):
            export(input_notebook_path=notebook_path, output_path=output_path)


def test_should_be_resilient_to_empty_notebook():
    with tempfile.TemporaryDirectory() as tmp:
        output_path = join(tmp, 'out.py')
        notebook_path = gen_notebook(nb_cells=0, tmp_dir=tmp,
                                     file_name='test.ipynb', docstring=None)
        export(input_notebook_path=notebook_path, output_path=output_path)
        assert exists(output_path)


def test_should_extract_docstring():
    """
        Test that different docstring format are well extracted
    """

    docstring_cell = '''
    # Some comments
    some_code = 12
    {}
    code = 'some code again'
    # And comment
    '''

    inline_doctsring = '""" An inline docstring """'
    docstring_wrapper = extract_docstring_and_param(
        docstring_cell.format(inline_doctsring))
    assert docstring_wrapper.params == ''
    assert docstring_wrapper.docstring_by_line == [inline_doctsring]

    inline_doctsring = '""" An inline docstring """ aa """ invalid """'
    with pytest.raises(MlVToolException):
        extract_docstring_and_param(docstring_cell.format(inline_doctsring))

    for multi_line in ('"""\n{}\n"""', '"""{}\n"""', '"""\n{}"""'):
        multilinedoc_string = multi_line.format('A multiline docstring'
                                                 '\nWithout param info\n')
        docstring_wrapper = extract_docstring_and_param(
            docstring_cell.format(multilinedoc_string))
        assert docstring_wrapper.params == ''
        assert docstring_wrapper.docstring_by_line == \
               multilinedoc_string.strip().split('\n')

    multiline_doctsring = '""" A multiline\n docstring """\naa ' \
                          '= 4\n""" invalid """'
    with pytest.raises(MlVToolException):
        extract_docstring_and_param(docstring_cell.format(multiline_doctsring))


def test_should_extract_docstring_parameters():
    """
        Test that different docstring format are well extracted
    """

    docstring_cell = '''
    # Some comments
    some_code = 12
    """
    :param str param1: Param1 description
    :param int param2:
    :param param3: Param3 description
    :param param4:
    """
    code = 'some code again'
    # And comment
    '''
    docstring_wrapper = extract_docstring_and_param(docstring_cell)

    assert docstring_wrapper.params == 'param1:str, param2:int, param3, param4'