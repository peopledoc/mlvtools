from os.path import join

import pytest

from mlvtools.exception import MlVToolException
from mlvtools.export_pipeline import MlExportPipeline


def test_should_raise_if_missing_dvc_meta_file_input():
    """
        Test command raise if dvc meta file input is missing
    """
    arguments = ['--dvc', './step12.dvc', '-o', './exported_pipeline', '-w', './']
    with pytest.raises(MlVToolException):
        MlExportPipeline().run(*arguments)


def test_should_raise_if_output_path_exist_and_no_force(work_dir, last_pipeline_step):
    """
        Test command raise if output path already exists and no force argument
    """
    pipeline_output = join(work_dir, 'exported_pipeline.sh')
    with open(pipeline_output, 'w') as fd:
        fd.write('')
    arguments = ['--dvc', last_pipeline_step, '-o', pipeline_output, '-w', work_dir]
    with pytest.raises(MlVToolException):
        MlExportPipeline().run(*arguments)


def test_should_overwrite_with_force_argument(work_dir, last_pipeline_step):
    """
        Test output paths are overwritten with force argument
    """
    pipeline_output = join(work_dir, 'exported_pipeline.sh')
    with open(pipeline_output, 'w') as fd:
        fd.write('')
    arguments = ['--dvc', last_pipeline_step, '-o', pipeline_output, '-w', work_dir, '--force']
    MlExportPipeline().run(*arguments)

    with open(pipeline_output, 'r') as fd:
        assert fd.read()
