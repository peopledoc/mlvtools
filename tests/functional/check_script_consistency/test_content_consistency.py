from os.path import join

import pytest

from mlvtools.check_script import IPynbCheckScript
from tests.helpers.utils import gen_notebook, write_conf


@pytest.fixture()
def ref_notebook_path(work_dir):
    notebook_path = gen_notebook(tmp_dir=work_dir, file_name='test.ipynb', docstring=None,
                                 cells=[('code', '# A Tag\nprint(\'poney\')'),
                                        ('comment', '# This is a comment'),
                                        ('code', 'def test():\n'
                                                 '  """This is a docstring"""\n'
                                                 '  print("hello")\n')])
    return notebook_path


@pytest.fixture()
def ref_script_content():
    return '''
#!/usr/bin/env python3
from typing import List
import argparse
def mlvtools_test():
    print('poney')
    # # This is a comment
    def test():
        """This is a docstring"""
        print("hello")
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command for script mlvtools_test')
    args = parser.parse_args()
    mlvtools_test()
'''


def test_should_check_consistency_and_exit_without_error(work_dir, ref_notebook_path, ref_script_content):
    """
        Test check consistency between a notebook and its script
        with diff only on blank lines and comments.
        Should exit without error.
    """
    script_path = join(work_dir, 'script.py')
    with open(script_path, 'w') as fd:
        fd.write(ref_script_content)

    arguments = ['-n', ref_notebook_path, '-s', script_path, '--working-directory', work_dir]
    with pytest.raises(SystemExit) as e:
        IPynbCheckScript().run(*arguments)
    assert e.value.code == 0


def test_should_check_consistency_and_exit_with_error(work_dir, ref_notebook_path, ref_script_content):
    """
        Test check consistency between a notebook and a different script.
        Should exit with error.
    """
    function_def = 'def mlvtools_test():'
    assert function_def in ref_script_content
    ref_script_content = ref_script_content.replace(function_def, 'def mlvtools_diff():')

    script_path = join(work_dir, 'script.py')
    with open(script_path, 'w') as fd:
        fd.write(ref_script_content)

    arguments = ['-n', ref_notebook_path, '-s', script_path, '--working-directory', work_dir]
    with pytest.raises(SystemExit) as e:
        IPynbCheckScript().run(*arguments)
    assert e.value.code != 0


def test_should_check_consistency_and_exit_with_error_if_same_but_diff_from_conf(work_dir, ref_notebook_path,
                                                                                 ref_script_content):
    """
        Test check consistency between a notebook and its script
        with diff only on blank lines and comments.
        Should exit with error.
            Discard a notebook cell changing conf ignore_keys
    """
    conf_path = join(work_dir, 'conf.json')
    write_conf(work_dir, conf_path, ignore_keys=['# A Tag'])

    script_path = join(work_dir, 'script.py')
    with open(script_path, 'w') as fd:
        fd.write(ref_script_content)

    arguments = ['-n', ref_notebook_path, '-s', script_path, '--conf-path', conf_path, '--working-directory', work_dir]
    with pytest.raises(SystemExit) as e:
        IPynbCheckScript().run(*arguments)
    assert e.value.code != 0
