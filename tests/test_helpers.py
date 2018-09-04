from mlvtool.helper import to_cmd_param, to_method_name, to_bash_variable, to_script_name


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
