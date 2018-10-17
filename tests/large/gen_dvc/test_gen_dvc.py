import stat
from os import stat as os_stat
from os.path import dirname, join, exists
from subprocess import check_call

CURRENT_DIR = dirname(__file__)


def test_should_gen_dvc_command_using_command_line(work_dir):
    """
        Test gen_dvc using command line
    """
    script_path = join(CURRENT_DIR, 'data', 'script.py')
    out_dvc_path = join(work_dir, 'out_dvc')
    check_call(['gen_dvc', '-i', script_path, '-o', out_dvc_path, '-w', work_dir])

    assert exists(out_dvc_path)
    assert stat.S_IMODE(os_stat(out_dvc_path).st_mode) == 0o755
