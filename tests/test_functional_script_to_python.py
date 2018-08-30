import stat
import tempfile
from os import stat as os_stat
from os.path import join, exists

from mlvtool.script_to_cmd import gen_commands


def test_should_generate_commands():
    """
        Test python and dvc bash commands are generated from python script with param specified
        in docstring. Ensure the output command syntax is valid.
    """
    with tempfile.TemporaryDirectory() as tmp:
        python_script = 'def my_funct(subset: str, rate: int):\n' \
                        '\t"""\n' \
                        ':param str input_file: the input file\n' \
                        ':param output_file: the output_file\n' \
                        ':param rate: the rate\n' \
                        ':param int retry:\n' \
                        ':dvc-in input_file: ./data/train_set.csv\n' \
                        ':dvc-out output_file: ./data/model.bin\n' \
                        ':dvc-out: ./data/other.txt\n' \
                        '\t"""\n' \
                        '\tprint(\'toto\')\n'

        script_path = join(tmp, 'script_python.py')
        with open(script_path, 'w') as fd:
            fd.write(python_script)

        py_cmd_path = join(tmp, 'py_cmd')
        dvc_cmd_path = join(tmp, 'dvc_cmd')
        gen_commands(script_path, py_cmd_path, src_dir=tmp, bash_output_path=dvc_cmd_path)

        assert exists(py_cmd_path)
        assert exists(dvc_cmd_path)
        assert stat.S_IMODE(os_stat(py_cmd_path).st_mode) == 0o755
        assert stat.S_IMODE(os_stat(dvc_cmd_path).st_mode) == 0o755

        # Ensure generated file syntax is right
        with open(py_cmd_path, 'r') as fd:
            compile(fd.read(), py_cmd_path, 'exec')

        # Ensure dvc command is in dvc bash command
        with open(dvc_cmd_path, 'r') as fd:
            dvc_bash_content = fd.read()

        assert 'dvc run' in dvc_bash_content
        assert '-o $OUTPUT_FILE' in dvc_bash_content
        assert '-o ./data/other.txt' in dvc_bash_content
        assert '-d $INPUT_FILE' in dvc_bash_content


def test_should_generate_dvc_with_whole_cmd():
    """
        Test dvc bash command is generated from python script with whole dvc command
        ad specified in docstring
    """
    with tempfile.TemporaryDirectory() as tmp:
        cmd = 'dvc run -o ./out_train.csv \n' \
              '-o ./out_test.csv\n' \
              './py_cmd -m train --out ./out_train.csv &&\n' \
              './py_cmd -m test --out ./out_test.csv'
        python_script = 'def my_funct(subset: str, rate: int):\n' \
                        '\t"""\n' \
                        ':param str input_file: the input file\n' \
                        ':param output_file: the output_file\n' \
                        f':dvc-cmd:{cmd}\n' \
                        '\t"""\n' \
                        '\tprint(\'toto\')\n'

        script_path = join(tmp, 'script_python.py')
        with open(script_path, 'w') as fd:
            fd.write(python_script)

        py_cmd_path = join(tmp, 'py_cmd')
        dvc_cmd_path = join(tmp, 'dvc_cmd')
        gen_commands(script_path, py_cmd_path, src_dir=tmp, bash_output_path=dvc_cmd_path)

        assert exists(dvc_cmd_path)

        # Ensure whole command is in dvc bash command
        with open(dvc_cmd_path, 'r') as fd:
            dvc_bash_content = fd.read()

        assert cmd.replace('\n', ' \\\n') in dvc_bash_content
