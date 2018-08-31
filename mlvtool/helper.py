import re
from collections import namedtuple


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
        match = re.match('^[L|l]ist(?:\[(?P<type_name>\w*)\])?$', type_name)
        if match:
            is_list = True
            type_name = 'str' if not match.group('type_name') else match.group('type_name')
        return TypeInfo(type_name, is_list)
    return TypeInfo(None, is_list=False)
