import stat
from os import stat as os_stat
from os.path import join, exists

from mlvtools.export_pipeline import MlExportPipeline


def test_should_generate_commands(work_dir, last_pipeline_step, expected_export_pipeline):
    """
        Test pipeline is exported as a bash script containing a call to all needed commands
        in the right order
    """

    exported_pipeline_path = join(work_dir, 'exported_pipeline.sh')
    arguments = ['--dvc', last_pipeline_step, '--output', exported_pipeline_path, '--work-dir', '/work_dir']
    MlExportPipeline().run(*arguments)

    with open(expected_export_pipeline, 'r') as fd:
        expected_res = [line.strip().strip('\n') for line in fd.readlines() if line.strip().strip('\n')]

    assert exists(exported_pipeline_path)
    with open(exported_pipeline_path, 'r') as fd:
        result = [line.strip().strip('\n') for line in fd.readlines() if line.strip().strip('\n')]

    assert expected_res == result
    assert stat.S_IMODE(os_stat(exported_pipeline_path).st_mode) == 0o755
