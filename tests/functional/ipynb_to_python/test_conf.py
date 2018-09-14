from os.path import join, exists
from typing import Tuple

from mlvtools.conf.conf import DEFAULT_CONF_FILENAME
from mlvtools.ipynb_to_python import IPynbToPython
from tests.helpers.utils import write_conf, gen_notebook


def setup_with_conf(work_dir: str, conf_path: str) -> Tuple[str, str]:
    write_conf(work_dir=work_dir, conf_path=conf_path, script_dir='./test_scripts')
    nb_path = gen_notebook(["# test"], work_dir, 'nb_test.ipynb')
    return conf_path, nb_path


def test_should_get_output_path_from_conf(work_dir):
    """
        Test output python script path is generated from notebook name and provided configuration
    """
    conf_path, notebook_path = setup_with_conf(work_dir, conf_path=join(work_dir, 'my_conf'))

    arguments = ['-n', notebook_path, '--working-directory', work_dir, '--conf-path', conf_path]
    IPynbToPython().run(*arguments)

    # Those path are generated using conf path and the notebook name
    script_path = join(work_dir, 'test_scripts', 'mlvtools_nb_test.py')
    assert exists(script_path)


def test_should_get_output_path_from_auto_detected_conf(work_dir):
    """
        Test output python script path is generated from notebook name and auto detected configuration
    """
    conf_path, notebook_path = setup_with_conf(work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME))

    arguments = ['-n', notebook_path, '--working-directory', work_dir]
    IPynbToPython().run(*arguments)

    # Those path are generated using conf path and the notebook name
    script_path = join(work_dir, 'test_scripts', 'mlvtools_nb_test.py')
    assert exists(script_path)


def test_should_overwrite_conf(work_dir):
    """
        Test output path argument overwrite conf
    """
    conf_path, notebook_path = setup_with_conf(work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME))

    arg_script_path = join(work_dir, 'custom_script.py')
    arguments = ['-n', notebook_path, '--working-directory', work_dir, '-o', arg_script_path]
    IPynbToPython().run(*arguments)

    # Assert output path is the one given as command argument not the one generated from conf
    assert exists(arg_script_path)
    conf_script_path = join(work_dir, 'test_scripts', 'nb_test.py')
    assert not exists(conf_script_path)
