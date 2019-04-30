import pytest

from mlvtools.check_script import IPynbCheckAllScripts
from mlvtools.exception import MlVToolException
from tests.helpers.utils import gen_notebook


def test_should_raise_if_no_conf(work_dir):
    """
        Test command raise if no conf, neither auto detected or given to command line
    """
    notebook_path = gen_notebook(cells=[('code', 'pass')], tmp_dir=work_dir, file_name='test_nb.ipynb')
    arguments = ['-n', notebook_path, '--working-directory', work_dir]
    with pytest.raises(MlVToolException):
        IPynbCheckAllScripts().run(*arguments)
