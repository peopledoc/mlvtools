import stat
from os import stat as os_stat, makedirs
from os.path import join, exists, basename, relpath

import pytest
import yaml

from mlvtools.exception import MlVToolException
from mlvtools.gen_dvc import MlScriptToCmd


def test_should_generate_commands(work_dir):
    """
        Test dvc bash command is generated from python script with param specified
        in docstring.
    """
    python_script = 'def my_funct(subset: str, rate: int):\n' \
                    '\t"""\n' \
                    ':param str input_file: the input file\n' \
                    ':param output_file: the output_file\n' \
                    ':param rate: the rate\n' \
                    ':param int retry:\n' \
                    ':param List[int] threshold:\n' \
                    ':dvc-in input_file: ./data/train_set.csv\n' \
                    ':dvc-out output_file: {{ conf.output_file }}\n' \
                    ':dvc-out: ./data/other.txt\n' \
                    '\t"""\n' \
                    '\tprint(\'toto\')\n'
    # Write python script
    script_path = join(work_dir, 'script_python.py')
    with open(script_path, 'w') as fd:
        fd.write(python_script)

    # Write docstring conf
    dc_conf_path = join(work_dir, 'dc_conf.yml')
    with open(dc_conf_path, 'w') as fd:
        yaml.dump({'output_file': './data/other.txt'}, fd)

    dvc_cmd_path = join(work_dir, 'dvc_cmd')
    arguments = ['-i', script_path, '--out-dvc-cmd', dvc_cmd_path, '--working-directory', work_dir,
                 '--docstring-conf', dc_conf_path]
    MlScriptToCmd().run(*arguments)

    assert exists(dvc_cmd_path)
    assert stat.S_IMODE(os_stat(dvc_cmd_path).st_mode) == 0o755

    # Ensure dvc command is in dvc bash command
    with open(dvc_cmd_path, 'r') as fd:
        dvc_bash_content = fd.read()

    assert 'OUTPUT_FILE="./data/other.txt"' in dvc_bash_content
    assert 'MLV_DVC_META_FILENAME="script_python.dvc"' in dvc_bash_content
    assert 'dvc run${NO_CACHE_OPT} --overwrite-dvcfile -f $MLV_DVC_META_FILENAME' in dvc_bash_content
    assert '-o $OUTPUT_FILE' in dvc_bash_content
    assert '-o ./data/other.txt' in dvc_bash_content
    assert '-d $INPUT_FILE' in dvc_bash_content


def test_should_generate_dvc_with_whole_cmd(work_dir):
    """
        Test dvc bash command is generated from python script with whole dvc command
        ad specified in docstring
    """
    cmd = 'dvc run -o ./out_train.csv \n' \
          '-o ./out_test.csv\n' \
          '$MLV_PY_CMD_PATH -m train --out ./out_train.csv &&\n' \
          './python/${MLV_PY_CMD_NAME} -m test --out ./out_test.csv'
    python_script = 'def my_funct(subset: str, rate: int):\n' \
                    '\t"""\n' \
                    ':param str input_file: the input file\n' \
                    ':param output_file: the output_file\n' \
                    f':dvc-cmd:{cmd}\n' \
                    '\t"""\n' \
                    '\tprint(\'toto\')\n'

    script_path = join(work_dir, 'script_python.py')
    with open(script_path, 'w') as fd:
        fd.write(python_script)

    makedirs(join(work_dir, 'python'))
    dvc_cmd_path = join(work_dir, 'dvc_cmd')
    arguments = ['-i', script_path, '--out-dvc-cmd', dvc_cmd_path, '--working-directory', work_dir]
    MlScriptToCmd().run(*arguments)

    assert exists(dvc_cmd_path)

    # Ensure whole command is in dvc bash command
    with open(dvc_cmd_path, 'r') as fd:
        dvc_bash_content = fd.read()

    relative_py_cmd_path = relpath(script_path, work_dir)

    assert f'MLV_PY_CMD_PATH="{relative_py_cmd_path}"' in dvc_bash_content
    assert f'MLV_PY_CMD_NAME="{basename(relative_py_cmd_path)}"' in dvc_bash_content
    assert cmd.replace('\n', ' \\\n') in dvc_bash_content


def test_generate_commands_should_raise_if_missing_variable(work_dir):
    """
        Test dvc bash command generation fails if a docstring template variable is missing
    """
    python_script = 'def my_funct(subset: str, rate: int):\n' \
                    '\t"""\n' \
                    ':param str locale: The data locale\n' \
                    ':param output_file: the output_file\n' \
                    ':dvc-out output_file: {{ conf.output_file }}\n' \
                    ':dvc-extra:  --locale {{ conf.locale }}\n' \
                    '\t"""\n' \
                    '\tprint(\'toto\')\n'
    # Write python script
    script_path = join(work_dir, 'script_python.py')
    with open(script_path, 'w') as fd:
        fd.write(python_script)

    # Write docstring conf
    dc_conf_path = join(work_dir, 'dc_conf.yml')
    with open(dc_conf_path, 'w') as fd:
        yaml.dump({'output_file': './data/other.txt'}, fd)

    dvc_cmd_path = join(work_dir, 'dvc_cmd')
    arguments = ['-i', script_path, '--out-dvc-cmd', dvc_cmd_path, '--working-directory', work_dir,
                 '--docstring-conf', dc_conf_path]

    with pytest.raises(MlVToolException):
        MlScriptToCmd().run(*arguments)
