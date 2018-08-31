import glob
import stat
import tempfile
from os import stat as os_stat, listdir
from os.path import join, exists

from pytest import fixture

from mlvtool.conf.conf import MlVToolConf, DEFAULT_CONF_FILENAME
from mlvtool.script_to_cmd import MlScriptToCmd
from tests.helpers.utils import write_conf


@fixture
def conf():
    return MlVToolConf(top_directory='./')


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
                        ':param List[int] threshold:\n' \
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
        arguments = ['-i', script_path, '--out-py-cmd', py_cmd_path, '--out-dvc-cmd', dvc_cmd_path,
                     '--working-directory', tmp]
        MlScriptToCmd().run(*arguments)

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


def write_min_script(script_path: str):
    python_script = 'def my_funct():\n' \
                    '\t""" A description """\n' \
                    '\tpass\n'
    with open(script_path, 'w') as fd:
        fd.write(python_script)


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
        arguments = ['-i', script_path, '--out-py-cmd', py_cmd_path, '--out-dvc-cmd', dvc_cmd_path,
                     '--working-directory', tmp]
        MlScriptToCmd().run(*arguments)

        assert exists(dvc_cmd_path)

        # Ensure whole command is in dvc bash command
        with open(dvc_cmd_path, 'r') as fd:
            dvc_bash_content = fd.read()

        assert cmd.replace('\n', ' \\\n') in dvc_bash_content


def test_should_generate_commands_with_provided_conf():
    """
        Test commands are generated from python script using provided configuration
    """
    with tempfile.TemporaryDirectory() as tmp:
        conf_path = join(tmp, 'my_conf')
        write_conf(work_dir=tmp, conf_path=conf_path, ignore_keys=['# Ignore'],
                   py_cmd_dir='./py_cmd', dvc_cmd_dir='./dvc_cmd')

        script_path = join(tmp, 'script_path.py')
        write_min_script(script_path)

        arguments = ['-i', script_path, '--working-directory', tmp, '--conf-path', conf_path]
        MlScriptToCmd().run(*arguments)

        # Those path are generated using conf path and the script name
        py_cmd_path = join(tmp, 'py_cmd', 'script_path')
        dvc_cmd_path = join(tmp, 'dvc_cmd', 'script_path_dvc')
        assert exists(py_cmd_path)
        assert exists(dvc_cmd_path)


def test_should_generate_commands_with_auto_detected_conf():
    """
        Test commands are generated from python script using auto detected configuration
    """
    with tempfile.TemporaryDirectory() as tmp:
        conf_path = join(tmp, DEFAULT_CONF_FILENAME)
        write_conf(work_dir=tmp, conf_path=conf_path, ignore_keys=['# Ignore'],
                   py_cmd_dir='./py_cmd', dvc_cmd_dir='./dvc_cmd')

        script_path = join(tmp, 'script_path.py')
        write_min_script(script_path)

        arguments = ['-i', script_path, '--working-directory', tmp]
        MlScriptToCmd().run(*arguments)

        # Those path are generated using conf path and the script name
        py_cmd_path = join(tmp, 'py_cmd', 'script_path')
        dvc_cmd_path = join(tmp, 'dvc_cmd', 'script_path_dvc')
        assert exists(py_cmd_path)
        assert exists(dvc_cmd_path)


def test_should_not_generate_dvc_command_if_disable_no_conf():
    """
        Test commands are generated from python script using auto detected configuration
    """
    with tempfile.TemporaryDirectory() as work_dir:
        script_path = join(work_dir, 'script_path.py')
        write_min_script(script_path)

        py_cmd_path = join(work_dir, 'py_cmd')
        arguments = ['-i', script_path, '--working-directory', work_dir, '--no-dvc', '--out-py-cmd', py_cmd_path]
        MlScriptToCmd().run(*arguments)

        # Only script and python cmd must be generated in work directory
        work_dir_content = listdir(work_dir)
        assert len(work_dir_content) == 2
        assert 'script_path.py' in work_dir_content
        assert 'py_cmd' in work_dir_content


def test_should_not_generate_dvc_command_if_disable_with_conf():
    """
        Test commands are generated from python script using auto detected configuration
    """
    with tempfile.TemporaryDirectory() as work_dir:
        conf_path = join(work_dir, DEFAULT_CONF_FILENAME)
        write_conf(work_dir=work_dir, conf_path=conf_path, ignore_keys=['# Ignore'],
                   py_cmd_dir='./py_cmd', dvc_cmd_dir='./dvc_cmd')

        script_path = join(work_dir, 'script_path.py')
        write_min_script(script_path)

        arguments = ['-i', script_path, '--working-directory', work_dir, '--no-dvc']
        MlScriptToCmd().run(*arguments)

        # Check no dvc file is generated
        dvc_file = glob.glob(join(work_dir, '**/*_dvc'))
        assert not dvc_file
