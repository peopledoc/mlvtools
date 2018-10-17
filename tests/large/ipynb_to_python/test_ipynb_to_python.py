import stat
from os import stat as os_stat
from os.path import dirname, join, exists
from subprocess import check_call

CURRENT_DIR = dirname(__file__)


def test_should_convert_to_python_script_using_command_line(work_dir):
    """
        Test ipynb_to_python using command line
    """
    notebook_path = join(CURRENT_DIR, 'data', 'notebook.ipynb')
    out_script_path = join(work_dir, 'out.py')
    check_call(['ipynb_to_python', '-n', notebook_path, '-o', out_script_path, '-w', work_dir])

    assert exists(out_script_path)
    assert stat.S_IMODE(os_stat(out_script_path).st_mode) == 0o755
