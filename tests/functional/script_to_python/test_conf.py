import glob
from os import listdir
from os.path import join, exists
from typing import Tuple

from mlvtools.conf.conf import DEFAULT_CONF_FILENAME
from mlvtools.script_to_cmd import MlScriptToCmd
from tests.helpers.utils import write_conf, write_min_script


def setup_with_conf(work_dir: str, conf_path: str) -> Tuple[str, str]:
    write_conf(work_dir=work_dir, conf_path=conf_path, ignore_keys=['# Ignore'],
               py_cmd_dir='./py_cmd', dvc_cmd_dir='./dvc_cmd')
    script_path = join(work_dir, 'script_path.py')
    write_min_script(script_path)
    return conf_path, script_path


def test_should_get_output_path_from_conf(work_dir):
    """
        Test commands are generated from python script using provided configuration
    """
    conf_path, script_path = setup_with_conf(work_dir, conf_path=join(work_dir, 'my_conf'))

    arguments = ['-i', script_path, '--working-directory', work_dir, '--conf-path', conf_path]
    MlScriptToCmd().run(*arguments)

    # Those path are generated using conf path and the script name
    py_cmd_path = join(work_dir, 'py_cmd', 'script_path')
    dvc_cmd_path = join(work_dir, 'dvc_cmd', 'script_path_dvc')
    assert exists(py_cmd_path)
    assert exists(dvc_cmd_path)


def test_should_get_output_path_from_auto_detected_conf(work_dir):
    """
        Test commands are generated from python script using auto detected configuration
    """
    conf_path, script_path = setup_with_conf(work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME))

    arguments = ['-i', script_path, '--working-directory', work_dir]
    MlScriptToCmd().run(*arguments)

    # Those path are generated using conf path and the script name
    py_cmd_path = join(work_dir, 'py_cmd', 'script_path')
    dvc_cmd_path = join(work_dir, 'dvc_cmd', 'script_path_dvc')
    assert exists(py_cmd_path)
    assert exists(dvc_cmd_path)


def test_should_not_generate_dvc_command_if_disable_no_conf(work_dir):
    """
        Test commands are generated from python script using auto detected configuration
    """
    script_path = join(work_dir, 'script_path.py')
    write_min_script(script_path)

    py_cmd_path = join(work_dir, 'py_cmd')
    arguments = ['-i', script_path, '--working-directory', work_dir, '--no-dvc', '--out-py-cmd', py_cmd_path]
    MlScriptToCmd().run(*arguments)

    # Only script and python cmd must be generated in work directory
    work_dir_content = listdir(work_dir)
    assert len(work_dir_content) == 2
    assert 'script_path.py' in work_dir_content
    assert 'py_cmd' in work_dir_content


def test_should_not_generate_dvc_command_if_disable_with_conf(work_dir):
    """
        Test commands are generated from python script using auto detected configuration
    """
    conf_path, script_path = setup_with_conf(work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME))

    arguments = ['-i', script_path, '--working-directory', work_dir, '--no-dvc']
    MlScriptToCmd().run(*arguments)

    # Check no dvc file is generated
    dvc_file = glob.glob(join(work_dir, '**/*_dvc'))
    assert not dvc_file


def test_should_overwrite_conf(work_dir):
    """
        Test output paths argument overwrite conf
    """
    conf_path, script_path = setup_with_conf(work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME))

    arg_dvc_cmd_path = join(work_dir, 'new_place_dvc')
    arguments = ['-i', script_path, '--working-directory', work_dir, '--out-dvc-cmd', arg_dvc_cmd_path]
    MlScriptToCmd().run(*arguments)

    # Assert output path are those from comma,nd argument not from conf
    assert exists(arg_dvc_cmd_path)
    conf_py_cmd_path = join(work_dir, 'py_cmd', 'script_path')
    assert exists(conf_py_cmd_path)
    conf_dvc_cmd_path = join(work_dir, 'dvc_cmd', 'script_path_dvc')
    assert not exists(conf_dvc_cmd_path)
