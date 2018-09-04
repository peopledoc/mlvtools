import tempfile
from os.path import realpath, dirname, join, exists

import pytest

from mlvtool.exception import MlVToolException
from mlvtool.ipynb_to_python import export, extract_docstring_and_param, \
    get_param_as_python_method_format, filter_no_effect
from tests.helpers.utils import gen_notebook

CURRENT_DIR = realpath(dirname(__file__))


def test_should_convert_notebook_to_python_script():
    """
        Test Notebook is converted to python script
    """
    with tempfile.TemporaryDirectory() as tmp:
        output_path = join(tmp, 'out.py')
        notebook_path = gen_notebook(cells=['print(\'poney\')'], tmp_dir=tmp,
                                     file_name='test.ipynb', docstring=None)
        export(input_notebook_path=notebook_path, output_path=output_path)

        assert exists(output_path)
        with open(output_path, 'r') as fd:
            content = fd.read()

        # Check main method is created
        assert 'def test():' in content


@pytest.mark.parametrize('header', (None, '#Big Title'))
def test_should_detect_parameters(header):
    """
        Test Notebook is converted to parameterized python script,
        parameter cell in Notebook is detected and well handled.
        The parameter cell must be the first code cell. It should be detected
        if there is a markdown header or not.
    """
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
        notebook_path = gen_notebook(cells=['print(\'poney\')'], tmp_dir=tmp,
                                     file_name='test.ipynb',
                                     docstring=docstring_cell,
                                     header=header)
        export(input_notebook_path=notebook_path, output_path=output_path)
        assert exists(output_path)
        with open(output_path, 'r') as fd:
            content = fd.read()

        # Check main method is created
        assert 'def test(subset: str, rate: int, param3):' in content


def test_should_raise_if_invalid_docstring():
    """
        Test an MlVTool exception is raised if docstring is invalid
    """
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

        notebook_path = gen_notebook(cells=['print(\'poney\')'], tmp_dir=tmp,
                                     file_name='test.ipynb',
                                     docstring=docstring_cell)
        with pytest.raises(MlVToolException):
            export(input_notebook_path=notebook_path, output_path=output_path)


def test_should_raise_if_more_than_one_docstring_in_first_cell():
    """
        Test multi docstring in the parameter cell is detected
    """
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

        notebook_path = gen_notebook(cells=['print(\'poney\')'], tmp_dir=tmp,
                                     file_name='test.ipynb',
                                     docstring=docstring_cell)
        with pytest.raises(MlVToolException):
            export(input_notebook_path=notebook_path, output_path=output_path)


def test_should_be_resilient_to_empty_notebook():
    """
        Test templating is resilient to empty Notebook, no exception.
    """
    with tempfile.TemporaryDirectory() as tmp:
        output_path = join(tmp, 'out.py')
        notebook_path = gen_notebook(cells=['print(\'poney\')'], tmp_dir=tmp,
                                     file_name='test.ipynb', docstring=None)
        export(input_notebook_path=notebook_path, output_path=output_path)
        assert exists(output_path)


def test_should_extract_parameters():
    """
        Test parameters are extracted from docstring with optional and
        mandatory fields
    """

    docstring_str = '''"""
    :param str param_one: Param1 description
    :param int param2:
    :param param3: Param3 description
    :param param4:
    """'''
    parameters = get_param_as_python_method_format(docstring_str)

    assert parameters == 'param_one: str, param2: int, param3, param4'


def test_should_extract_docstring_and_params():
    """
        Test docstring and parameters are well extracted
    """
    docstring = '''"""
:param str param1: Param1 description
:param int param2:
:param param3: Param3 description
:param param4:
"""'''
    docstring_cell = f'''
# Some comments
{docstring}
code = 'some code again'
# And comment
    '''
    docstring_wrapper = extract_docstring_and_param(docstring_cell)
    assert docstring_wrapper.params == 'param1: str, param2: int, param3, param4'
    assert docstring_wrapper.docstring == docstring


def test_should_discard_cell():
    """
        Test that cell containing #No effect statement are discarded
    """
    standard_cell = '''
    #This is a comment but not a No effect
    value = 15
    '''
    assert filter_no_effect(standard_cell) == standard_cell

    no_effect_cell = '''
    #This is a comment but not a No effect
    # No effect
    big_res = big_call()
    '''
    assert filter_no_effect(no_effect_cell) == ''
