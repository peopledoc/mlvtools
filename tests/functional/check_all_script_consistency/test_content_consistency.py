from os import makedirs, remove
from os.path import join, basename

import pytest

from mlvtools.check_script import IPynbCheckAllScripts
from tests.helpers.utils import gen_notebook, write_conf


@pytest.fixture()
def notebook_dir(work_dir):
    notebook_dir = join(work_dir, 'notebooks')
    makedirs(notebook_dir)
    gen_notebook(tmp_dir=notebook_dir, file_name='hello.ipynb', docstring=None,
                 cells=[('comment', '# This is a comment for hello'),
                        ('code', 'print("hello")'),
                        ('code', '# A Tag\nprint("end")')])
    gen_notebook(tmp_dir=notebook_dir, file_name='hi.ipynb', docstring=None,
                 cells=[('comment', '# This is a comment for hi'),
                        ('code', 'print("hi")'),
                        ('code', '# A Tag\nprint("end")')])
    gen_notebook(tmp_dir=notebook_dir, file_name='bye.ipynb', docstring=None,
                 cells=[('comment', '# This is a comment for bye'),
                        ('code', 'print("bye")'),
                        ('code', '# A Tag\nprint("end")')])
    return notebook_dir


def write_script(path: str, content: str):
    name = basename(path).replace('.py', '')
    script_content = f'''
#!/usr/bin/env python3
import argparse
def {name}():
    {content}
    print("end")
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command for script {name}')
    args = parser.parse_args()
    {name}()
'''
    with open(path, 'w') as fd:
        fd.write(script_content)


@pytest.fixture()
def script_dir(work_dir):
    script_dir = join(work_dir, 'scripts')
    makedirs(script_dir)
    write_script(join(script_dir, 'mlvtools_hello.py'), 'print("hello")')
    write_script(join(script_dir, 'mlvtools_hi.py'), 'print("hi")')
    write_script(join(script_dir, 'mlvtools_bye.py'), 'print("bye")')
    return script_dir


def test_should_check_consistency_for_all_notebooks_from_directory_and_exit_without_error(work_dir,
                                                                                          notebook_dir,
                                                                                          script_dir):
    """
        Test check consistency for all notebooks from a given directory.
        Should exit without error.
        Ignore other file from the given directory.
    """
    conf_path = join(work_dir, 'conf.json')
    write_conf(work_dir, conf_path, script_dir=script_dir, dvc_cmd_dir=work_dir)

    # Add noise: a text file in notebook directory
    with open(join(notebook_dir, 'text_file.txt'), 'w') as fd:
        fd.write('some text')

    arguments = ['-n', notebook_dir, '-c', conf_path, '--working-directory', work_dir]
    with pytest.raises(SystemExit) as e:
        IPynbCheckAllScripts().run(*arguments)
    assert e.value.code == 0


def test_should_check_consistency_for_nb_from_dir_and_exit_with_error_if_dif_from_conf(work_dir,
                                                                                       notebook_dir,
                                                                                       script_dir):
    """
        Test check consistency for all notebooks from a given directory.
        Should exit with error.
            Discard a notebook cell changing conf ignore_keys
    """
    conf_path = join(work_dir, 'conf.json')
    write_conf(work_dir, conf_path, script_dir=script_dir, dvc_cmd_dir=work_dir, ignore_keys=['# A Tag'])

    arguments = ['-n', notebook_dir, '-c', conf_path, '--working-directory', work_dir]
    with pytest.raises(SystemExit) as e:
        IPynbCheckAllScripts().run(*arguments)
    assert e.value.code != 0


def test_should_check_consistency_for_all_notebooks_from_directory_and_exit_with_error(work_dir,
                                                                                       notebook_dir,
                                                                                       script_dir):
    """
        Test check consistency for all notebooks from a given directory.
        Should exit with error due to one inconsistency.
    """
    conf_path = join(work_dir, 'conf.json')
    write_conf(work_dir, conf_path, script_dir=script_dir, dvc_cmd_dir=work_dir)

    # Overwrite one valid script
    write_script(join(script_dir, 'mlvtools_bye.py'), 'print("A different thing")')

    arguments = ['-n', notebook_dir, '-c', conf_path, '--working-directory', work_dir]
    with pytest.raises(SystemExit) as e:
        IPynbCheckAllScripts().run(*arguments)
    assert e.value.code != 0


def test_exit_with_error_if_a_script_is_missing(work_dir, notebook_dir, script_dir):
    """
         Test check consistency exits with error if a script is missing.
    """
    conf_path = join(work_dir, 'conf.json')
    write_conf(work_dir, conf_path, script_dir=script_dir, dvc_cmd_dir=work_dir)

    # Remove a valid script
    remove(join(script_dir, 'mlvtools_bye.py'))

    arguments = ['-n', notebook_dir, '-c', conf_path, '--working-directory', work_dir]
    with pytest.raises(SystemExit) as e:
        IPynbCheckAllScripts().run(*arguments)
    assert e.value.code != 0


def test_exit_without_error_if_a_script_is_inconsistent_but_ignored(work_dir, notebook_dir, script_dir):
    """
         Test check consistency exits without error if inconsistent script is ignored
    """
    conf_path = join(work_dir, 'conf.json')
    write_conf(work_dir, conf_path, script_dir=script_dir, dvc_cmd_dir=work_dir)

    # Overwrite one valid script
    write_script(join(script_dir, 'mlvtools_bye.py'), 'print("A different thing")')

    arguments = ['-n', notebook_dir, '-c', conf_path, '--working-directory', work_dir, '-i', 'bye.ipynb']
    with pytest.raises(SystemExit) as e:
        IPynbCheckAllScripts().run(*arguments)
    assert e.value.code == 0
