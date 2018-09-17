import itertools
import json
from json import JSONDecodeError
from os import makedirs
from os.path import join

import pytest

from mlvtools.conf.conf import MlVToolConf, get_script_output_path, \
    get_dvc_cmd_output_path, get_conf_file_default_path, DEFAULT_CONF_FILENAME, get_work_directory, \
    load_conf_or_default
from mlvtools.exception import MlVToolConfException, MlVToolException
from tests.helpers.utils import write_conf


def test_should_load_conf_file(work_dir):
    """ Test load valid conf file """

    conf_file = join(work_dir, '.mlvtools')
    write_conf(work_dir=work_dir, conf_path=conf_file, ignore_keys=['# No effect', "# Ignore"],
               script_dir='./scripts', dvc_cmd_dir='./dvc_cmd',
               dvc_py_cmd_name='VAR_Name', dvc_py_cmd_path='var_PATh3',
               dvc_meta_file_name='mETA_VAR_NaME')

    conf = load_conf_or_default(conf_file, working_directory=work_dir)

    assert conf.path.python_script_root_dir == './scripts'
    assert conf.path.dvc_cmd_root_dir == './dvc_cmd'
    assert '# No effect' in conf.ignore_keys
    assert '# Ignore' in conf.ignore_keys
    assert conf.dvc_var_python_cmd_path == 'var_PATh3'
    assert conf.dvc_var_python_cmd_name == 'VAR_Name'
    assert conf.dvc_var_meta_filename == 'mETA_VAR_NaME'

    script_path = join(conf.path.python_script_root_dir, 'mlvtools_pipeline_part1.py')
    assert get_script_output_path('./data/Pipeline Part1.ipynb', conf) == join(work_dir, script_path)
    dvc_cmd_path = join(conf.path.dvc_cmd_root_dir, 'pipeline_part1_dvc')
    assert get_dvc_cmd_output_path('./data/pipeline_part1.py', conf) == join(work_dir, dvc_cmd_path)


def test_should_raise_if_path_not_found(work_dir):
    """ Test raise if at least one path does not exists"""
    existing_path = join(work_dir, 'exists')
    makedirs(existing_path)
    wrong_path = './does_not_exist'
    conf_data = {
        'path': {
            'python_script_root_dir': '',
            'dvc_cmd_root_dir': ''
        },
        'ignore_keys': ['# No effect', "# Ignore"],
    }
    conf_file = join(work_dir, '.mlvtools')
    permutations = set(itertools.permutations([existing_path] * (len(conf_data['path']) - 1) + [wrong_path]))
    for perm in permutations:
        for i, path_name in enumerate(conf_data['path']):
            conf_data['path'][path_name] = perm[i]
        with open(conf_file, 'w') as fd:
            json.dump(conf_data, fd)
        with pytest.raises(MlVToolConfException):
            MlVToolConf.load_from_file(conf_file, working_directory=work_dir)


def test_should_raise_if_dvc_invalid_dvc_variable_name(work_dir):
    """ Test raise if dvc variable names are valid """
    existing_path = join(work_dir, 'exists')
    makedirs(existing_path)
    conf_data = {
        'dvc_var_python_cmd_path': '',
        'dvc_var_python_cmd_name': '',
        'dvc_var_meta_filename': ''
    }
    conf_file = join(work_dir, '.mlvtools')

    for invalid_var, valid_var_1, valid_var_2 in itertools.permutations(conf_data.keys()):
        conf_data[valid_var_1] = 'A_Valid_var67_name'
        conf_data[valid_var_1] = 'A_Valid_var67_name'
        for invalid_value in ('258_alphanum', '44test', 'with spaces ', 'This_is(_My_var', '#zz', '$rrr'):
            conf_data[invalid_var] = invalid_value
            with open(conf_file, 'w') as fd:
                json.dump(conf_data, fd)
            with pytest.raises(MlVToolConfException):
                MlVToolConf.load_from_file(conf_file, working_directory=work_dir)


def test_should_raise_if_conf_file_does_not_exist():
    """ Test raise if conf file does not exist"""

    with pytest.raises(MlVToolConfException) as e:
        MlVToolConf.load_from_file('./does_not.exist', working_directory='./')
    assert isinstance(e.value.__cause__, FileNotFoundError)


def test_should_raise_if_wrong_conf_file_format(work_dir):
    """ Test raise if wrong conf file format"""

    conf_file = join(work_dir, '.mlvtools')
    with open(conf_file, 'wb') as fd:
        fd.write(b'uueonrhfiss988#')
    with pytest.raises(MlVToolConfException) as e:
        MlVToolConf.load_from_file(conf_file, working_directory=work_dir)
    assert isinstance(e.value.__cause__, JSONDecodeError)


def test_should_get_default_conf_file_path():
    """
        Test get default configuration file path
    """
    conf_file_path = get_conf_file_default_path(work_dir='test')
    assert conf_file_path == join('test', DEFAULT_CONF_FILENAME)


def test_should_get_work_directory(work_dir, mocker):
    """
        Test get working directory from git
    """
    makedirs(join(work_dir, 'data'))
    input_file = join(work_dir, 'data' 'test.ipynb')
    with open(input_file, 'wb') as fd:
        fd.write(b'')

    mocked_check_output = mocker.patch('subprocess.check_output', return_value=work_dir.encode())

    work_directory = get_work_directory(input_file)

    assert work_directory == work_dir
    assert mocked_check_output.mock_calls == [mocker.call(
        ['git', 'rev-parse', '--show-toplevel'],
        cwd=work_dir)]


def test_should_raise_if_input_file_does_not_exist():
    """
        Test get working directory raise if input file doesn't exist
    """
    with pytest.raises(MlVToolException):
        get_work_directory('./does_not_exit.ipynb')
