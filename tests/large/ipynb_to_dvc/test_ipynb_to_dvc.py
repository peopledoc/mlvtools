import glob
import stat
from os import stat as os_stat
from os.path import dirname, join, exists
from subprocess import check_call

from mlvtools.conf.conf import DEFAULT_CONF_FILENAME
from tests.helpers.utils import write_conf

CURRENT_DIR = dirname(__file__)


def test_should_convert_to_python_script_using_command_line(work_dir):
    """
        Test ipynb_to_python using command line
    """
    dvc_dir = join(work_dir, 'dvc')
    script_dir = join(work_dir, 'scripts')
    write_conf(work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME),
               script_dir=script_dir, dvc_cmd_dir=dvc_dir)
    notebook_path = join(CURRENT_DIR, 'data', 'notebook.ipynb')
    check_call(['ipynb_to_dvc', '-n', notebook_path, '-w', work_dir])

    assert exists(script_dir)
    script_dir_content = glob.glob(join(script_dir, 'mlvtools*.py'))
    assert len(script_dir_content) == 1
    assert stat.S_IMODE(os_stat(script_dir_content[0]).st_mode) == 0o755

    assert exists(script_dir)
    dvc_dir_content = glob.glob(join(dvc_dir, 'mlvtools*_dvc'))
    assert len(dvc_dir_content) == 1
    assert stat.S_IMODE(os_stat(dvc_dir_content[0]).st_mode) == 0o755
