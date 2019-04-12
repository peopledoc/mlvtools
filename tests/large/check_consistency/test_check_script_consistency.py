from os.path import dirname, join
from subprocess import check_call, call

from mlvtools.conf.conf import DEFAULT_CONF_FILENAME
from tests.helpers.utils import write_conf

CURRENT_DIR = dirname(__file__)


def test_should_detect_consistency_for_notebook_and_script(work_dir):
    """
        Test check_script_consistency exit without error when there is consistency
        between notebook and script
    """
    notebook_path = join(CURRENT_DIR, 'data', 'notebooks', 'notebook_blank_and_comment_diff.ipynb')
    script_path = join(CURRENT_DIR, 'data', 'script_no_blank_no_comment.py')

    check_call(['check_script_consistency', '-n', notebook_path, '-s', script_path, '-w', work_dir])


def test_should_detect_inconsistency_for_notebook_and_script(work_dir):
    """
        Test check_script_consistency exit with error when there is inconsistency
        between notebook and script.
    """
    notebook_path = join(CURRENT_DIR, 'data', 'notebooks', 'notebook_blank_and_comment_diff.ipynb')
    script_path = join(CURRENT_DIR, 'data', 'script_no_blank_no_comment_disable_cell.py')

    ret_code = call(['check_script_consistency', '-n', notebook_path, '-s', script_path, '-w', work_dir])
    assert ret_code != 0


def test_should_detect_consistency_for_notebook_and_script_with_conf(work_dir):
    """
        Test check_script_consistency exit without error when there is consistency
        between notebook and script with conf.

        Without conf there is inconsistency but with the right ignore cell there is consistency
    """
    notebook_path = join(CURRENT_DIR, 'data', 'notebooks', 'notebook_blank_and_comment_diff.ipynb')
    script_path = join(CURRENT_DIR, 'data', 'script_no_blank_no_comment_disable_cell.py')

    write_conf(work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME), ignore_keys=['# A Tag'])

    check_call(['check_script_consistency', '-n', notebook_path, '-s', script_path, '-w', work_dir])
