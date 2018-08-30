import re


def to_cmd_param(variable: str) -> str:
    """
        Convert a variable in a command parameter format
    """
    return variable.lower().replace('_', '-')


def to_bash_variable(param: str) -> str:
    """
        Convert a command variable in a bash variable
    """
    return param.upper().replace('-', '_')


def to_method_name(name: str) -> str:
    """
        Convert a file name without extension to a python method name
    """
    return re.sub('\W+', '_', name).lower()


def to_script_name(file_name: str) -> str:
    return file_name.replace('.ipynb', '').replace(' ', '_').lower()
