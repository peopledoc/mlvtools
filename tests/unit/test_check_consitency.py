from os.path import join

import pytest
from pytest import fixture

from mlvtools.check_script import compare
from mlvtools.conf.conf import MlVToolConf
from mlvtools.exception import MlVToolException
from mlvtools.helper import write_python_script
from mlvtools.ipynb_to_python import export_to_script
from tests.helpers.utils import gen_notebook


@fixture
def conf():
    return MlVToolConf(top_directory='./')


def create_notebook_and_convert_it(cells, script_name, conf, work_dir) -> str:
    """
        Create a notebook from cells then convert it into a python script
    """
    notebook_path = gen_notebook(tmp_dir=work_dir, file_name='test.ipynb', docstring=None, cells=cells)
    script_base_path = join(work_dir, script_name)
    export_to_script(notebook_path, script_base_path, conf)
    return notebook_path, script_base_path


def test_should_find_consistency_between_notebook_and_script_from_itself(conf, work_dir):
    """
        Test there is consistency between a notebook and its own script conversion
    """
    cells = [('code', 'print(\'poney\')'),
             ('comment', '# This is a comment'),
             ('code', 'def test():\n  """This is a docstring"""\n  print("hello")\n')]
    notebook_path, script_path = create_notebook_and_convert_it(cells, 'script.py', conf, work_dir)

    assert compare(notebook_path, script_path, conf)


def test_should_find_consistency_between_notebook_and_script_with_diff_empty_line(conf, work_dir):
    """
        Test there is consistency between a notebook and a script. Ignore empty_lines
    """
    notebook_path = gen_notebook(tmp_dir=work_dir, file_name='test.ipynb', docstring=None,
                                 cells=[('code', 'print(\'poney\')'),
                                        ('comment', '# This is a comment'),
                                        ('code', 'def test():\n'
                                                 '  """This is a docstring"""\n'
                                                 '  print("hello")\n')])
    script_content = '''
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
    script_path = join(work_dir, 'script.py')
    write_python_script(script_content, script_path)

    assert compare(notebook_path, script_path, conf)


def test_should_find_consistency_with_diff_on_comments(conf, work_dir):
    """
        Test there is consistency with diff only on comments
    """
    cells = [('code', 'print(\'poney\')'),
             ('comment', '# This is a comment'),
             ('code', 'def test():\n  """Thsaved_notebok_base_pathis is a docstring"""\n  print("hello")\n')]
    _, script_base_path = create_notebook_and_convert_it(cells, 'base.py', conf, work_dir)

    cells[1] = ('comment', '# This is a DIFFERENT comment')
    notebook_diff_path = gen_notebook(tmp_dir=work_dir, file_name='test.ipynb', docstring=None, cells=cells)

    assert compare(notebook_diff_path, script_base_path, conf)


def test_should_detect_inconsistency_with_diff_script(conf, work_dir):
    """
        Test detects inconsistency with diff script
    """
    cells = [('code', 'print(\'poney\')'),
             ('comment', '# This is a comment'),
             ('code', 'def test():\n  """This is a docstring"""\n  print("hello")\n')]
    _, script_base_path = create_notebook_and_convert_it(cells, 'a.py', conf, work_dir)

    cells[0] = ('code', 'print("diff")')
    notebook_diff_path = gen_notebook(tmp_dir=work_dir, file_name='test.ipynb', docstring=None, cells=cells)

    assert not compare(notebook_diff_path, script_base_path, conf)


def test_should_detect_inconsistency_with_script_from_same_nb_diff_conf(conf, work_dir):
    """
        Test detects inconsistency due to a diff conf
    """
    cells = [('code', '# Discard conf A\nprint(\'conf A\')'),
             ('code', '# Discard conf B\nprint(\'conf B\')')]
    conf.ignore_keys = ['# Discard conf A']
    notebook_path, script_path = create_notebook_and_convert_it(cells, 'script.py', conf, work_dir)

    conf.ignore_keys = ['# Discard conf B']
    assert not compare(notebook_path, script_path, conf)


def test_should_raise_if_notebook_is_not_a_file(conf, work_dir):
    """
        Test raises if provided notebook is not a file
    """
    script_path = join(work_dir, 'script.py')
    write_python_script('import os', script_path)
    with pytest.raises(MlVToolException) as e:
        compare(join(work_dir, 'does_not_exist.ipynb'), script_path, conf)
    assert isinstance(e.value.__cause__, IOError)


def test_should_raise_if_script_is_not_a_file(conf, work_dir):
    """
        Test raises if provided script is not a file
    """
    cells = [('code', 'a = 3')]
    notebook_path = gen_notebook(tmp_dir=work_dir, file_name='test.ipynb', docstring=None, cells=cells)

    with pytest.raises(MlVToolException) as e:
        compare(notebook_path, join(work_dir, 'does_not_exist.py'), conf)
    assert isinstance(e.value.__cause__, IOError)


def test_should_raise_if_invalid_script(conf, work_dir):
    """
        Test raises if provided script is not a file
    """
    cells = [('code', 'a = 3')]
    notebook_path = gen_notebook(tmp_dir=work_dir, file_name='test.ipynb', docstring=None, cells=cells)
    script_path = join(work_dir, 'script.py')
    with open(script_path, 'w') as fd:
        fd.write('a:=3')
    with pytest.raises(MlVToolException) as e:
        compare(notebook_path, script_path, conf)
    assert isinstance(e.value.__cause__, SyntaxError)
