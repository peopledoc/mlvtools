from os.path import realpath, dirname, basename

from docstring_parser import parse as dc_parse

from mlvtools.script_to_cmd import DocstringInfo, get_dvc_template_data

CURRENT_DIR = realpath(dirname(__file__))


def test_should_get_dvc_param_from_docstring():
    """Test dvc parameters are extracted from docstring"""
    repr = ':param str param-one: Param1 description\n' \
           ':param param2: input file\n' \
           ':dvc-out: path/to/file.txt\n' \
           ':dvc-out param-one: path/to/other\n' \
           ':dvc-in param2: path/to/in/file\n' \
           ':dvc-in: path/to/other/infile.test\n' \
           ':dvc-extra: --train --rate 12'
    docstring_info = DocstringInfo(method_name='my_method',
                                   docstring=dc_parse(repr),
                                   repr=repr,
                                   file_path='/data/my_prj/python/my_file.py')
    python_cmd_path = '/script/python/test_cmd'
    extra_var = {'MLV_PY_CMD_PATH': python_cmd_path, 'MLV_PY_CMD_NAME': basename(python_cmd_path)}
    info = get_dvc_template_data(docstring_info, python_cmd_path, extra_variables=extra_var)

    expected_info = {
        'variables': [f'MLV_PY_CMD_PATH="{python_cmd_path}"', f'MLV_PY_CMD_NAME="{basename(python_cmd_path)}"',
                      'PARAM2="path/to/in/file"', 'PARAM_ONE="path/to/other"'],
        'dvc_inputs': ['$PARAM2', 'path/to/other/infile.test'],
        'dvc_outputs': ['path/to/file.txt', '$PARAM_ONE'],
        'python_params': '--param2 $PARAM2 --param-one $PARAM_ONE --train --rate 12',
        'python_script': python_cmd_path,
    }
    assert expected_info.keys() == info.keys()

    assert sorted(expected_info['variables']) == sorted(info['variables'])
    assert sorted(expected_info['dvc_inputs']) == sorted(info['dvc_inputs'])
    assert sorted(expected_info['dvc_outputs']) == sorted(info['dvc_outputs'])
    assert sorted(expected_info['python_params'].split(' ')) == sorted(info['python_params'].split(' '))
    assert expected_info['python_script'] == info['python_script']


def test_should_get_dvc_cmd_param_from_docstring():
    """Test dvc parameters are extracted from docstring"""
    cmd = 'dvc run -o ./out_train.csv \n' \
          '-o ./out_test.csv\n' \
          './py_cmd -m train --out ./out_train.csv &&\n' \
          './py_cmd -m test --out ./out_test.csv'
    repr = ':param str param-one: Param1 description\n' \
           ':param param2: input file\n' \
           f':dvc-cmd: {cmd}'
    docstring_info = DocstringInfo(method_name='my_method',
                                   docstring=dc_parse(repr),
                                   repr=repr,
                                   file_path='/data/my_prj/python/my_file.py')
    python_cmd_path = '../script/python/test_cmd'
    info = get_dvc_template_data(docstring_info, python_cmd_path)

    assert len(info.keys()) == 2
    assert info['whole_command'] == cmd.replace('\n', ' \\\n')
    assert not info['variables']
