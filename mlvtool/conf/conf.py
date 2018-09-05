import json
import logging
from json import JSONDecodeError
from os.path import join, exists, basename, dirname
from typing import List

from pydantic import BaseModel, validator, ValidationError

from mlvtool.exception import MlVToolConfException, MlVToolException
from mlvtool.helper import to_script_name, to_py_cmd_name, to_dvc_cmd_name, get_git_top_dir

DEFAULT_CONF_FILENAME = '.mlvtool'

DEFAULT_IGNORE_KEY = '# No effect'


class MlVToolPathConf(BaseModel):
    python_script_root_dir: str
    python_cmd_root_dir: str
    dvc_cmd_root_dir: str


class MlVToolConf(BaseModel):
    path: MlVToolPathConf = None
    ignore_keys: List[str] = [DEFAULT_IGNORE_KEY]
    top_directory: str

    @validator('top_directory', pre=True)
    def top_directory_exists(cls, value, values, config, field):
        if not exists(value):
            raise MlVToolConfException(f'Configuration error {field.name}, can not find top directory {value}')
        cls.top_directory = value
        return value

    @validator('path')
    def directories_exits(cls, value):
        for field in value.fields:
            path = getattr(value, field)
            if not exists(join(cls.top_directory, path)):
                raise MlVToolConfException(f'Configuration error {field}, can not find directory {path}')
        return value

    @staticmethod
    def get_top_directory_raw_data(top_dir: str) -> dict:
        return {'top_directory': top_dir}

    @staticmethod
    def load_from_file(file_path: str, working_directory) -> 'MlVToolConf':
        try:
            with open(file_path, 'r') as fd:
                conf_raw_data = json.load(fd)
            conf_raw_data.update(MlVToolConf.get_top_directory_raw_data(working_directory))
            return MlVToolConf.parse_obj(conf_raw_data)
        except JSONDecodeError as e:
            raise MlVToolConfException(f'Cannot load conf from file {file_path}. Wrong format') from e
        except ValidationError as e:
            raise MlVToolConfException(f'Cannot load conf from file {file_path}. Validation error') from e
        except IOError as e:
            raise MlVToolConfException(f'Cannot load conf from file {file_path}') from e


def load_conf_or_default(conf_path: str, working_directory) -> MlVToolConf:
    """ Load the configuration file if present """
    if exists(conf_path):
        return MlVToolConf.load_from_file(conf_path, working_directory)
    logging.warning('No configuration found. Use default')
    return MlVToolConf(top_directory=working_directory)


def get_script_output_path(notebook_path: str, conf: MlVToolConf) -> str:
    """ Generate python script path according to conf and notebook file name """
    file_name = to_script_name(basename(notebook_path))
    return join(conf.top_directory, conf.path.python_script_root_dir, file_name)


def get_python_cmd_output_path(script_path: str, conf: MlVToolConf) -> str:
    """ Generate python command path according to conf and python script file name """
    file_name = to_py_cmd_name(basename(script_path))
    return join(conf.top_directory, conf.path.python_cmd_root_dir, file_name)


def get_dvc_cmd_output_path(script_path: str, conf: MlVToolConf) -> str:
    """ Generate dvc command path according to conf and python script file name """
    file_name = to_dvc_cmd_name(basename(script_path))
    return join(conf.top_directory, conf.path.dvc_cmd_root_dir, file_name)


def get_work_directory(input_path: str) -> str:
    if not exists(input_path):
        raise MlVToolException(f'Input file {input_path} does not exist.')
    return get_git_top_dir(dirname(input_path))


def get_conf_file_default_path(work_dir: str) -> str:
    return join(work_dir, DEFAULT_CONF_FILENAME)
