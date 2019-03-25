import logging
import re
from collections import namedtuple
from os import chmod, makedirs
from os.path import splitext, basename, dirname

import subprocess
from jinja2 import TemplateError, StrictUndefined, UndefinedError
from jinja2.environment import Environment
from typing import List
from yapf.yapflib.yapf_api import FormatCode

from mlvtools.exception import MlVToolException

MLV_PREFIX = 'mlvtools_'
MAX_LINE_LENGTH = 120


def to_cmd_param(variable: str) -> str:
    """
        Convert a variable in a command parameter format
    """
    return variable.replace('_', '-')


def to_bash_variable(param: str) -> str:
    """
        Convert a command variable in a bash variable
    """
    return param.upper().replace('-', '_')


def to_method_name(name: str) -> str:
    """
        Convert a file name without extension to a python method name
    """
    return '{}{}'.format(MLV_PREFIX, to_lower_alphanum(name))


def to_script_name(file_name: str) -> str:
    """
        Return a python script name deduced from a notebook file name
    """
    without_extension = splitext(file_name)[0]
    return '{}{}.py'.format(MLV_PREFIX, to_lower_alphanum(without_extension))


def to_lower_alphanum(file_name_no_ext: str):
    """
        Convert a file name without extension to a lower case alphanumeric filename
    """
    return re.sub(r'\W+', '_', file_name_no_ext).lower()


def to_dvc_cmd_name(script_name: str) -> str:
    """
        Return a dvc command name deduced from a python script name
    """
    return '{}_dvc'.format(splitext(script_name)[0])


def to_dvc_meta_filename(python_script_path: str) -> str:
    """
        Return a dvc meta file name deduced from a python script path
    """
    without_extension = splitext(python_script_path)[0]
    return f'{to_lower_alphanum(basename(without_extension))}.dvc'


def to_instructions_list(source: str) -> List[str]:
    """
        Convert a string of several instruction into a list of instructions
    """
    return source.strip('\n').split('\n')


def to_sanitized_path(path: str):
    """ Ensure path starts with / """
    return path if path.startswith(('/', './')) else f'./{path}'


def get_git_top_dir(cwd: str) -> str:
    try:
        return subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=cwd) \
            .decode() \
            .strip('\n')
    except subprocess.SubprocessError as e:
        message = 'Can not run \'git rev-parse\' command to get top directory. Input files must belong ' \
                  'to a git repository.'
        logging.fatal(message)
        raise MlVToolException(message) from e


TypeInfo = namedtuple('TypeInfo', ('type_name', 'is_list'))


def extract_type(type_name: str) -> TypeInfo:
    """
        Extract type info (type name and is list) from docstring
        type.
        examples:
            str => str, is_list=False
            int => int, is_list=False
            List[int] => int, is_list=True
            list[str] => str, is_list=True

    """
    if type_name:
        is_list = False
        type_name = type_name.strip()
        match = re.match(r'^[L|l]ist(?:\[(?P<type_name>\w*)\])?$', type_name)
        if match:
            is_list = True
            type_name = 'str' if not match.group('type_name') else match.group('type_name')
        return TypeInfo(type_name, is_list)
    return TypeInfo(None, is_list=False)


def render_string_template(string_template: str, **kwargs) -> str:
    """
        Render a Jinja string template
    """
    return Environment(undefined=StrictUndefined).from_string(string_template).render(**kwargs)


def write_template(output_path, template_path: str, **kwargs):
    """
        Write an executable output file using Jinja template.
    """
    logging.info(f'Write command {output_path} using template {basename(template_path)}')
    try:
        makedirs(dirname(output_path), exist_ok=True)
        with open(template_path, 'r') as template_fd, open(output_path, 'w') as fd:
            content = render_string_template(template_fd.read(), **kwargs)
            fd.write(content)
        chmod(output_path, 0o755)
    except IOError as e:
        raise MlVToolException(f'Cannot create executable {output_path} using template {template_path}') from e
    except UndefinedError as e:
        raise MlVToolException(f'Cannot render {output_path} using template {template_path} due to undefined '
                               f'variable: {e}') from e
    except TemplateError as e:
        raise MlVToolException(f'Cannot render {output_path} using template {template_path}') from e


def write_python_script(script_content: str, output_path: str):
    """
        Write Python 3 generated code into an executable file
        - use yapf for code format
    """
    try:
        makedirs(dirname(output_path), exist_ok=True)
        formatted_script = FormatCode(script_content, style_config=f'{{ based_on_style: pep8, '
                                                                   f'column_limit: {MAX_LINE_LENGTH} }}')
        with open(output_path, 'w') as fd:
            fd.write(formatted_script[0])
        chmod(output_path, 0o755)
    except SyntaxError as e:
        raise MlVToolException(f'Cannot write generated Python, content is wrongly formatted: {script_content}') from e
    except IOError as e:
        raise MlVToolException(f'Cannot write generated Python script {output_path}') from e
