import stat
from os import stat as os_stat
from os.path import dirname, join, exists
from subprocess import check_call

CURRENT_DIR = dirname(__file__)


def test_should_export_pipeline_command_using_command_line(work_dir):
    """
        Test export_pipeline using command line
    """
    dvc_target = join(CURRENT_DIR, 'data', 'mlvtools_step5_sort_data.dvc')
    pipeline_out_path = join(work_dir, 'pipeline.sh')
    check_call(['export_pipeline', '--dvc', dvc_target, '-o', pipeline_out_path, '-w', work_dir])

    assert exists(pipeline_out_path)
    assert stat.S_IMODE(os_stat(pipeline_out_path).st_mode) == 0o755
