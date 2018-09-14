from os.path import join, exists

from mlvtools.conf.conf import DEFAULT_CONF_FILENAME
from mlvtools.ipynb_to_python import IPynbToPython
from tests.helpers.utils import gen_notebook
from tests.helpers.utils import write_conf


def test_should_handle_notebook_with_invalid_python_name_with_conf(work_dir, mocker):
    """
        Test invalid python filename are converted
    """
    mocked_check_output = mocker.patch('subprocess.check_output', return_value=work_dir.encode())
    notebook_path = gen_notebook(cells=['pass'], tmp_dir=work_dir, file_name='01_(test) nb.ipynb')

    # Create conf in a freshly init git repo
    conf_data = write_conf(work_dir=work_dir, conf_path=join(work_dir, DEFAULT_CONF_FILENAME),
                           ignore_keys=['# Ignore', 'remove='])

    cmd_arguments = ['-n', notebook_path]
    IPynbToPython().run(*cmd_arguments)

    # This path is generated using the conf script_dir and the notebook name
    output_script_path = join(work_dir, conf_data['path']['python_script_root_dir'], 'mlvtools_01__test_nb.py')
    assert exists(output_script_path)

    with open(output_script_path, 'r') as fd:
        file_content = fd.read()

    # Ensure generated file syntax is right
    compile(file_content, output_script_path, 'exec')

    assert mocked_check_output.mock_calls == [mocker.call(
        ['git', 'rev-parse', '--show-toplevel'],
        cwd=work_dir)]
