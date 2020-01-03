import stat
import os

from pathlib import Path

import pytest
import yaml
from subprocess import check_call

CURRENT_DIR = os.path.dirname(__file__)


def test_should_gen_dvc_command_using_command_line(work_dir):
    """
        Test gen_dvc using command line
    """
    script_path = os.path.join(CURRENT_DIR, 'data', 'script.py')
    out_dvc_path = os.path.join(work_dir, 'out_dvc')
    check_call(['gen_dvc', '-i', script_path, '-o', out_dvc_path, '-w', work_dir])

    assert os.path.exists(out_dvc_path)
    assert stat.S_IMODE(os.stat(out_dvc_path).st_mode) == 0o755


def test_should_generate_dvc_command_if_path_does_not_start_with_slash(work_dir):
    """
        Test generate the dvc command does not fail if output path does not start with slash
    """
    script_path = os.path.join(CURRENT_DIR, 'data', 'script.py')
    output_path = 'out_dvc'
    check_call(['gen_dvc', '-i', script_path, '-o', output_path, '-w', work_dir], cwd=work_dir)

    assert os.path.exists(os.path.join(work_dir, output_path))


@pytest.mark.parametrize('output_path', ('./existing_sub_dir/out_dvc', './new_sub_dir/out_dvc'))
def test_should_generate_dvc_command_even_if_sub_dir_exists(work_dir, output_path):
    """
        Test generate the dvc command does not fail if sub_directory exists
    """
    script_path = os.path.join(CURRENT_DIR, 'data', 'script.py')
    output_path = os.path.join(work_dir, output_path)
    os.makedirs(os.path.join(work_dir, 'existing_sub_dir'))
    check_call(['gen_dvc', '-i', script_path, '-o', output_path, '-w', work_dir])

    assert os.path.exists(output_path)


def test_dvc_command_cache_can_be_disabled(work_dir):
    """
        Test a generated dvc command can be re-run without cache
        - Create a DVC command using gen_dvc and a docstring conf
            This command call through DVC a 'write_name.py' script.
            The output of this script is tracked by DVC.
            This script has a side effect (which is bad), it does not write the
            same thing in the output even without input change (it is done for test purpose)
        - Initialize a Git/DVC environment
        - Run the generated DVC command
        - Re-run using cache and check nothing has changed
        - Re-run without cache and check output content has changed (which means the associated script
        is really re-run and the side effect can happen)
    """

    # Write DVC command docstring conf to specify output_file and name
    docstring_conf_file = os.path.join(work_dir, 'docstring.conf')
    input_file = os.path.join(work_dir, 'input')
    output_file = os.path.join(work_dir, 'test.out')
    Path(input_file).touch()
    with open(docstring_conf_file, 'w') as fd:
        yaml.dump({
            'input_file': input_file,
            'output_file': output_file,
            'name': 'Bob'},
            fd)

    # Generate DVC command for write_name.py script
    script_path = os.path.join(CURRENT_DIR, 'data', 'write_name.py')
    dvc_cmd = os.path.join(work_dir, 'dvc_cmd')
    check_call(['gen_dvc', '-i', script_path, '-o', dvc_cmd, '-w', work_dir, '--docstring-conf', docstring_conf_file])

    # Run the DVC command once
    check_call(['git', 'init'], cwd=work_dir)
    check_call(['dvc', 'init'], cwd=work_dir)

    check_call(dvc_cmd, cwd=work_dir)
    assert os.path.exists(output_file)
    with open(output_file) as fd:
        assert fd.read() == 'Hello Bob! First run'

    # Re-run using cache then assert nothing as changed
    check_call(dvc_cmd, cwd=work_dir)
    assert os.path.exists(output_file)
    with open(output_file) as fd:
        assert fd.read() == 'Hello Bob! First run'

    # Re-run without cache then assert side effect happened
    check_call([f'yes | {dvc_cmd} --no-cache'], shell=True, cwd=work_dir)
    assert os.path.exists(output_file)
    with open(output_file) as fd:
        assert fd.read() == 'Hello Bob! Not the first run'
