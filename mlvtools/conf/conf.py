import json
import logging
import re
from json import JSONDecodeError
from os.path import join, exists, basename
from typing import List

import yaml
from pydantic import BaseModel, validator, ValidationError, root_validator

from mlvtools.exception import MlVToolConfException
from mlvtools.helper import to_script_name, to_dvc_cmd_name, to_dvc_meta_filename

DEFAULT_CONF_FILENAME = '.mlvtools'

DEFAULT_IGNORE_KEY = '# No effect'


class MlVToolPathConf(BaseModel):
    python_script_root_dir: str
    dvc_cmd_root_dir: str
    dvc_metadata_root_dir: str = "."


class MlVToolConf(BaseModel):
    path: MlVToolPathConf = None
    ignore_keys: List[str] = [DEFAULT_IGNORE_KEY]
    top_directory: str
    dvc_var_python_cmd_path: str = 'MLV_PY_CMD_PATH'
    dvc_var_python_cmd_name: str = 'MLV_PY_CMD_NAME'
    dvc_var_meta_filename: str = 'MLV_DVC_META_FILENAME'
    docstring_conf: str = None

    @validator('dvc_var_python_cmd_path', 'dvc_var_python_cmd_name', 'dvc_var_meta_filename')
    def is_valid_var_name(cls, value, values, config, field):
        if not re.match(r'^[a-zA-Z]\w*$', value):
            raise MlVToolConfException(f'Configuration error {field.name} must be a valid bash variable name : {value}')
        return value

    @validator('top_directory', pre=True)
    def top_directory_exists(cls, value, values, config, field):
        if not exists(value):
            raise MlVToolConfException(f'Configuration error {field.name}, can not find top directory {value}')
        cls.top_directory = value
        return value

    @root_validator
    def directories_exists(cls, values):
        paths = values["path"]
        if not paths:
            return values
        top_directory = values["top_directory"]
        for field in paths.fields:
            path = getattr(paths, field)
            if not exists(join(top_directory, path)):
                raise MlVToolConfException(f'Configuration error {field}, can not find directory {path}')
        return values

    @root_validator
    def set_docstring_conf_path(cls, values):
        if values["docstring_conf"]:
            values["docstring_conf"] = join(values["top_directory"], values["docstring_conf"])
        return values

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
        logging.info(f'Load configuration from {conf_path}')
        return MlVToolConf.load_from_file(conf_path, working_directory)
    logging.info('No configuration found. Use default.')
    return MlVToolConf(top_directory=working_directory)


def get_script_output_path(notebook_path: str, conf: MlVToolConf) -> str:
    """ Generate python script path according to conf and notebook file name """
    file_name = to_script_name(basename(notebook_path))
    return join(conf.top_directory, conf.path.python_script_root_dir, file_name)


def get_dvc_cmd_output_path(script_path: str, conf: MlVToolConf) -> str:
    """ Generate dvc command path according to conf and python script file name """
    file_name = to_dvc_cmd_name(basename(script_path))
    return join(conf.top_directory, conf.path.dvc_cmd_root_dir, file_name)


def get_dvc_metadata_output_path(script_path: str, conf: MlVToolConf) -> str:
    """ Generate dvc metadata path according to conf and python script file name """
    file_name = to_dvc_meta_filename(basename(script_path))
    return join(conf.top_directory, conf.path.dvc_metadata_root_dir, file_name)


def get_conf_file_default_path(work_dir: str) -> str:
    return join(work_dir, DEFAULT_CONF_FILENAME)


def load_docstring_conf(docstring_conf_path: str) -> dict:
    """ Load a Yaml format docstring configuration """
    try:
        logging.info(f'Load docstring configuration from {docstring_conf_path}')
        with open(docstring_conf_path, 'r') as fd:
            return yaml.safe_load(fd)
    except yaml.YAMLError as e:
        raise MlVToolConfException(f'Cannot load docstring conf {docstring_conf_path}. Format error {e}.') from e
    except IOError as e:
        raise MlVToolConfException(f'Cannot load file {docstring_conf_path}. IOError {e}') from e
