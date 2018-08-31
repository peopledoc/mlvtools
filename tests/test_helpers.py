from mlvtool.helper import to_cmd_param, to_method_name, to_bash_variable, to_script_name, extract_type


def test_should_convert_to_command_param():
    """
        Test convert to command parameter
    """
    assert to_cmd_param('my_param_one') == 'my-param-one'


def test_should_convert_to_bash_variable():
    """
        Test convert to bash variable
    """
    assert to_bash_variable('my-param-one') == 'MY_PARAM_ONE'


def test_should_convert_to_method_name():
    """
        Test convert file name without extension to a python method name
    """
    assert to_method_name('my-Meth$od\k++ Name.truc') == 'my_meth_od_k_name_truc'


def test_should_convert_to_script_name():
    """
        Test convert file name to script name
    """
    assert to_script_name('My notebook.ipynb') == 'my_notebook'


def test_should_extract_python_str_and_int():
    """
        Test extract python str and int types
    """
    type_info = extract_type('str ')
    assert type_info.type_name == 'str'
    assert not type_info.is_list
    type_info = extract_type(' int')
    assert type_info.type_name == 'int'
    assert not type_info.is_list


def test_should_return_none_if_extract_python_of_no_type():
    """
        Test extract python return None if empty type
    """
    type_info = extract_type('')
    assert not type_info.type_name
    assert not type_info.is_list
    type_info = extract_type(None)
    assert not type_info.type_name
    assert not type_info.is_list


def test_should_extract_python_list_type():
    """
        Test extract python list type
    """
    type_info = extract_type('list')
    assert type_info.type_name == 'str'
    assert type_info.is_list
    type_info = extract_type('List')
    assert type_info.type_name == 'str'
    assert type_info.is_list

    type_info = extract_type('list[str]')
    assert type_info.type_name == 'str'
    assert type_info.is_list
    type_info = extract_type('List[int]')
    assert type_info.type_name == 'int'
    assert type_info.is_list
