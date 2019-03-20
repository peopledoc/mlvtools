import stat
from os import stat as os_stat, makedirs
from os.path import dirname, join, exists

import pytest
from subprocess import check_call
from yapf.yapflib.yapf_api import FormatCode

CURRENT_DIR = dirname(__file__)


def test_should_convert_to_python_script_using_command_line(work_dir):
    """
        Test ipynb_to_python using command line
        - Python script exists
        - Python script is executable
        - Python script is Pep8 compliant

    """
    notebook_path = join(CURRENT_DIR, 'data', 'notebook.ipynb')
    out_script_path = join(work_dir, 'out.py')
    check_call(['ipynb_to_python', '-n', notebook_path, '-o', out_script_path, '-w', work_dir])

    assert exists(out_script_path)
    assert stat.S_IMODE(os_stat(out_script_path).st_mode) == 0o755

    with open(out_script_path, 'r') as fd:
        _, has_changed = FormatCode(fd.read(), style_config='{based_on_style: pep8, column_limit: 120}')
    assert not has_changed


def test_should_convert_to_python_script_if_path_does_not_start_with_slash(work_dir):
    """
        Test convert to python script does not fail if output path does not start with slash
    """
    notebook_path = join(CURRENT_DIR, 'data', 'notebook.ipynb')
    output_path = 'out.py'
    check_call(['ipynb_to_python', '-n', notebook_path, '-o', 'out.py', '-w', work_dir], cwd=work_dir)
    assert exists(join(work_dir, output_path))


@pytest.mark.parametrize('output_path', ('./existing_sub_dir/out.py', './new_sub_dir/out.py'))
def test_should_convert_to_python_script_even_if_sub_dir_exists(work_dir, output_path):
    """
        Test convert to python script does not fail if sub_directory exists/ creates if does not exits
    """
    notebook_path = join(CURRENT_DIR, 'data', 'notebook.ipynb')
    output_path = join(work_dir, output_path)
    makedirs(join(work_dir, 'existing_sub_dir'))
    check_call(['ipynb_to_python', '-n', notebook_path, '-o', output_path, '-w', work_dir])

    assert exists(output_path)
