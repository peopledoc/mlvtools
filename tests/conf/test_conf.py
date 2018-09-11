import itertools
import json
import subprocess
import tempfile
from json import JSONDecodeError
from os import makedirs
from os.path import join

import pytest

from mlvtools.conf.conf import MlVToolConf, get_script_output_path, get_python_cmd_output_path, \
    get_dvc_cmd_output_path, get_conf_file_default_path, DEFAULT_CONF_FILENAME, get_work_directory, \
    load_conf_or_default
from mlvtools.exception import MlVToolConfException, MlVToolException
from tests.helpers.utils import write_conf


def test_should_load_conf_file():
    """ Test load valid conf file """

    with tempfile.TemporaryDirectory() as work_dir:
        conf_file = join(work_dir, '.mlvtools')
        write_conf(work_dir=work_dir, conf_path=conf_file, ignore_keys=['# No effect', "# Ignore"],
                   script_dir='./scripts', py_cmd_dir='./py_cmd', dvc_cmd_dir='./dvc_cmd',
                   dvc_py_cmd_name='VAR_Name', dvc_py_cmd_path='var_PATh3')

        conf = load_conf_or_default(conf_file, working_directory=work_dir)

        assert conf.path.python_script_root_dir == './scripts'
        assert conf.path.python_cmd_root_dir == './py_cmd'
        assert conf.path.dvc_cmd_root_dir == './dvc_cmd'
        assert '# No effect' in conf.ignore_keys
        assert '# Ignore' in conf.ignore_keys
        assert conf.dvc_var_python_cmd_path == 'var_PATh3'
        assert conf.dvc_var_python_cmd_name == 'VAR_Name'

        script_path = join(conf.path.python_script_root_dir, 'mlvtools_pipeline_part1.py')
        assert get_script_output_path('./data/Pipeline Part1.ipynb', conf) == join(work_dir, script_path)
        py_cmd_path = join(conf.path.python_cmd_root_dir, 'pipeline_part1')
        assert get_python_cmd_output_path('./data/pipeline_part1.py', conf) == join(work_dir, py_cmd_path)
        dvc_cmd_path = join(conf.path.dvc_cmd_root_dir, 'pipeline_part1_dvc')
        assert get_dvc_cmd_output_path('./data/pipeline_part1.py', conf) == join(work_dir, dvc_cmd_path)


def test_should_raise_if_path_not_found():
    """ Test raise if at least one path does not exists"""

    with tempfile.TemporaryDirectory() as tmp:
        existing_path = join(tmp, 'exists')
        makedirs(existing_path)
        wrong_path = './does_not_exist'
        conf_data = {
            'path': {
                'python_script_root_dir': '',
                'python_cmd_root_dir': '',
                'dvc_cmd_root_dir': ''
            },
            'ignore_keys': ['# No effect', "# Ignore"],
        }
        conf_file = join(tmp, '.mlvtools')
        permutations = set(itertools.permutations([existing_path] * (len(conf_data['path']) - 1) + [wrong_path]))
        for perm in permutations:
            for i, path_name in enumerate(conf_data['path']):
                conf_data['path'][path_name] = perm[i]
            with open(conf_file, 'w') as fd:
                json.dump(conf_data, fd)
            with pytest.raises(MlVToolConfException):
                MlVToolConf.load_from_file(conf_file, working_directory=tmp)


def test_should_raise_if_dvc_invalid_dvc_variable_name():
    """ Test raise if dvc variable names are valid """

    with tempfile.TemporaryDirectory() as tmp:
        existing_path = join(tmp, 'exists')
        makedirs(existing_path)
        conf_data = {
            'dvc_var_python_cmd_path': '',
            'dvc_var_python_cmd_name': '',
        }
        conf_file = join(tmp, '.mlvtools')

        # ^[a-z][a-zA-Z0-9_]*$
        for invalid_var, valid_var in itertools.permutations(conf_data.keys()):
            conf_data[valid_var] = 'A_Valid_var67_name'
            for invalid_value in ('258_alphanum', '44test', 'with spaces ', 'This_is(_My_var', '#zz', '$rrr'):
                conf_data[invalid_var] = invalid_value
                with open(conf_file, 'w') as fd:
                    json.dump(conf_data, fd)
                with pytest.raises(MlVToolConfException):
                    MlVToolConf.load_from_file(conf_file, working_directory=tmp)


def test_should_raise_if_conf_file_does_not_exist():
    """ Test raise if conf file does not exist"""

    with pytest.raises(MlVToolConfException) as e:
        MlVToolConf.load_from_file('./does_not.exist', working_directory='./')
    assert isinstance(e.value.__cause__, FileNotFoundError)


def test_should_raise_if_wrong_conf_file_format():
    """ Test raise if wrong conf file format"""

    with tempfile.TemporaryDirectory() as tmp:
        conf_file = join(tmp, '.mlvtools')
        with open(conf_file, 'wb') as fd:
            fd.write(b'uueonrhfiss988#')
        with pytest.raises(MlVToolConfException) as e:
            MlVToolConf.load_from_file(conf_file, working_directory=tmp)
        assert isinstance(e.value.__cause__, JSONDecodeError)


def test_should_get_default_conf_file_path():
    """
        Test get default configuration file path
    """
    conf_file_path = get_conf_file_default_path(work_dir='test')
    assert conf_file_path == join('test', DEFAULT_CONF_FILENAME)


def test_should_get_work_directory():
    """
        Test get working directory
    """
    with tempfile.TemporaryDirectory() as tmp:
        makedirs(join(tmp, 'data'))
        input_file = join(tmp, 'data' 'test.ipynb')
        with open(input_file, 'wb') as fd:
            fd.write(b'')
        subprocess.check_output(['git', 'init'], cwd=tmp)
        work_directory = get_work_directory(input_file)
        assert work_directory == tmp


def test_should_raise_if_input_file_does_not_exist():
    """
        Test get working directory raise if input file doesn't exist
    """
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.check_output(['git', 'init'], cwd=tmp)
        with pytest.raises(MlVToolException):
            get_work_directory('./does_not_exit.ipynb')
