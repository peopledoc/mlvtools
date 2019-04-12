import shutil
from os import listdir
from os.path import dirname, join
from subprocess import check_call, call

from mlvtools.conf.conf import DEFAULT_CONF_FILENAME
from tests.helpers.utils import write_conf

CURRENT_DIR = dirname(__file__)


def test_should_detect_consistency_for_notebooks(work_dir):
    """
        Test check_all_scripts_consistency exit without error when there is consistency
        between all notebooks and scripts from the provided directory
    """
    notebook_dir = join(CURRENT_DIR, 'data', 'notebooks')
    script_dir = join(CURRENT_DIR, 'data', 'script_dir')
    write_conf(work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME),
               script_dir=script_dir, dvc_cmd_dir=work_dir)
    check_call(['check_all_scripts_consistency', '-n', notebook_dir, '-w', work_dir])


def temporary_setup(work_dir):
    notebook_original_dir = join(CURRENT_DIR, 'data', 'notebooks')
    notebook_dir = join(work_dir, 'notebooks')
    script_original_dir = join(CURRENT_DIR, 'data', 'script_dir')
    script_dir = join(work_dir, 'script_dir')
    shutil.copytree(notebook_original_dir, notebook_dir)
    shutil.copytree(script_original_dir, script_dir)
    return notebook_dir, script_dir


def test_should_detect_inconsistency_if_at_least_one_inconsistent_script(work_dir):
    """
        Test check_all_scripts_consistency exit with error if there is at least one inconsistency
    """
    notebook_dir, script_dir = temporary_setup(work_dir)

    # Replace a script content
    with open(join(script_dir, listdir(script_dir)[0]), 'w') as fd:
        fd.write('print("Hello world!")')

    write_conf(work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME),
               script_dir=script_dir, dvc_cmd_dir=work_dir)

    ret_code = call(['check_all_scripts_consistency', '-n', notebook_dir, '-w', work_dir])
    assert ret_code != 0


def test_should_detect_ignore_notebooks(work_dir):
    """
        Test check_all_scripts_consistency exit with error if there is at least one inconsistency
    """
    notebook_dir, script_dir = temporary_setup(work_dir)

    # Replace the script which correspond to notebook.ipynb
    with open(join(script_dir, 'mlvtools_notebook.py'), 'w') as fd:
        fd.write('print("Hello world!")')

    # Duplicate a notebook with an other name so there is no associated script
    shutil.copy(join(notebook_dir, 'notebook.ipynb'), join(notebook_dir, 'new_nb.ipynb'))

    write_conf(work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME),
               script_dir=script_dir, dvc_cmd_dir=work_dir)

    # Ignore notebook.ipynb and new_nb.ipynb
    check_call(['check_all_scripts_consistency', '-n', notebook_dir, '-w', work_dir,
                '-i', 'notebook.ipynb', '-i', 'new_nb.ipynb'])
