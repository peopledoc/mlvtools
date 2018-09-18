from os.path import join, exists
from typing import Tuple

from mlvtools.conf.conf import DEFAULT_CONF_FILENAME
from mlvtools.gen_dvc import MlScriptToCmd
from tests.helpers.utils import write_conf, write_min_script


def setup_with_conf(work_dir: str, conf_path: str) -> Tuple[str, str]:
    write_conf(work_dir=work_dir, conf_path=conf_path, ignore_keys=['# Ignore'],
               dvc_cmd_dir='./dvc_cmd')
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

    # This path is generated using conf path and the script name
    dvc_cmd_path = join(work_dir, 'dvc_cmd', 'script_path_dvc')
    assert exists(dvc_cmd_path)


def test_should_get_output_path_from_auto_detected_conf(work_dir):
    """
        Test commands are generated from python script using auto detected configuration
    """
    conf_path, script_path = setup_with_conf(work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME))

    arguments = ['-i', script_path, '--working-directory', work_dir]
    MlScriptToCmd().run(*arguments)

    # This path is generated using conf path and the script name
    dvc_cmd_path = join(work_dir, 'dvc_cmd', 'script_path_dvc')
    assert exists(dvc_cmd_path)


def test_should_overwrite_conf(work_dir):
    """
        Test output paths argument overwrite conf
    """
    conf_path, script_path = setup_with_conf(work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME))

    arg_dvc_cmd_path = join(work_dir, 'new_place_dvc')
    arguments = ['-i', script_path, '--working-directory', work_dir, '--out-dvc-cmd', arg_dvc_cmd_path]
    MlScriptToCmd().run(*arguments)

    # Assert output path is the one from command argument not from conf
    assert exists(arg_dvc_cmd_path)
    conf_dvc_cmd_path = join(work_dir, 'dvc_cmd', 'script_path_dvc')
    assert not exists(conf_dvc_cmd_path)
