from os.path import join, exists
from typing import Tuple

import yaml

from mlvtools.conf.conf import DEFAULT_CONF_FILENAME
from mlvtools.gen_dvc import MlScriptToCmd
from tests.helpers.utils import write_conf, write_min_script


def write_docstring_conf(path: str, output_file: str):
    with open(path, 'w') as fd:
        yaml.dump({'out_file': output_file}, fd)


def setup_with_conf(work_dir: str, conf_path: str = None, docstring_conf_path: str = None) -> Tuple[str, str]:
    write_conf(work_dir=work_dir, conf_path=conf_path, ignore_keys=['# Ignore'],
               dvc_cmd_dir='./dvc_cmd', docstring_conf=docstring_conf_path)
    script_path = join(work_dir, 'script_path.py')
    docstring = '"""\n:param out:\n:dvc-out out: {{ conf.out_file }}\n"""' if docstring_conf_path else None
    write_min_script(script_path, docstring)
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


def test_should_get_docstring_conf_from_main_conf(work_dir):
    """
        Test docstring template values are replaced with docstring conf provided in main conf file
    """
    conf_dc_conf_path = join(work_dir, 'conf_dc_path.yml')
    write_docstring_conf(conf_dc_conf_path, './output_file_base.txt')
    conf_path, script_path = setup_with_conf(work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME),
                                             docstring_conf_path=conf_dc_conf_path)

    dvc_cmd_path = join(work_dir, 'new_place_dvc')
    arguments = ['-i', script_path, '--working-directory', work_dir, '--out-dvc-cmd', dvc_cmd_path]
    MlScriptToCmd().run(*arguments)

    # Assert docstring template value are replaced with the docstring conf content
    with open(dvc_cmd_path, 'r') as fd:
        content = fd.read()
    assert './output_file_base.txt' in content


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


def test_should_overwrite_conf_for_path(work_dir):
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


def test_should_overwrite_conf_for_docstring_conf(work_dir):
    """
        Test main configuration is overwritten for docstring conf selection
    """
    conf_dc_conf_path = join(work_dir, 'conf_dc_path.yml')
    write_docstring_conf(conf_dc_conf_path, './output_file_base.txt')
    conf_path, script_path = setup_with_conf(work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME),
                                             docstring_conf_path=conf_dc_conf_path)

    new_dc_conf_path = join(work_dir, 'new_dc_path.yml')
    write_docstring_conf(new_dc_conf_path, './output_file_overwritten.txt')

    dvc_cmd_path = join(work_dir, 'new_place_dvc')
    arguments = ['-i', script_path, '--working-directory', work_dir, '--docstring-conf', new_dc_conf_path,
                 '--out-dvc-cmd', dvc_cmd_path]
    MlScriptToCmd().run(*arguments)

    # Assert docstring template value are replaced with the right conf content
    with open(dvc_cmd_path, 'r') as fd:
        content = fd.read()
    assert './output_file_base.txt' not in content
    assert './output_file_overwritten.txt' in content
