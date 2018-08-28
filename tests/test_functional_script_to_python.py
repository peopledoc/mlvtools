import tempfile
from os.path import join, exists

from mlvtool.script_to_cmd import gen_python_script, TEMPLATE_NAME


def test_should_generate_python_command():
    """
        Test python command is generated from python script with param specifiec
        in docstring. Ensure the output command syntax is valid.
    """
    with tempfile.TemporaryDirectory() as tmp:
        python_script = 'def my_funct(subset: str, rate: int):\n' \
                        '\t"""\n' \
                        ':param str input_file: the input file\n' \
                        ':param output_file: the output_file\n' \
                        ':param rate: the rate\n' \
                        ':param int retry:\n' \
                        '\t"""\n' \
                        '\tprint(\'toto\')\n'

        script_path = join(tmp, 'script_python.py')
        with open(script_path, 'w') as fd:
            fd.write(python_script)

        cmd_path = join(tmp, 'py_cmd')
        gen_python_script(script_path, cmd_path, src_dir=tmp,
                          template_name=TEMPLATE_NAME)

        assert exists(cmd_path)

        # Ensure generated file syntax is right
        with open(cmd_path, 'r') as fd:
            compile(fd.read(), cmd_path, 'exec')
