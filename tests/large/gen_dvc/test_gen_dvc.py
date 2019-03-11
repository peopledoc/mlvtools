import stat
from os import stat as os_stat
from os.path import dirname, join, exists
from subprocess import check_call

import yaml

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
    docstring_conf_file = join(work_dir, 'docstring.conf')
    output_file = join(work_dir, 'test.out')
    with open(docstring_conf_file, 'w') as fd:
        yaml.dump({'output_file': output_file,
                   'name': 'Bob'},
                  fd)

    # Generate DVC command for write_name.py script
    script_path = join(CURRENT_DIR, 'data', 'write_name.py')
    dvc_cmd = join(work_dir, 'dvc_cmd')
    check_call(['gen_dvc', '-i', script_path, '-o', dvc_cmd, '-w', work_dir, '--docstring-conf', docstring_conf_file])

    # Run the DVC command once
    check_call(['git', 'init'], cwd=work_dir)
    check_call(['dvc', 'init'], cwd=work_dir)

    check_call(dvc_cmd, cwd=work_dir)
    assert exists(output_file)
    with open(output_file) as fd:
        assert fd.read() == 'Hello Bob! First run'

    # Re-run using cache then assert nothing as changed
    check_call(dvc_cmd, cwd=work_dir)
    assert exists(output_file)
    with open(output_file) as fd:
        assert fd.read() == 'Hello Bob! First run'

    # Re-run without cache then assert side effect happened
    check_call([f'yes | {dvc_cmd} --no-cache'], shell=True, cwd=work_dir)
    assert exists(output_file)
    with open(output_file) as fd:
        assert fd.read() == 'Hello Bob! Not the first run'
