import tempfile
from os.path import join, dirname

from pytest import fixture


@fixture
def work_dir():
    with tempfile.TemporaryDirectory() as work_dir:
        yield work_dir


@fixture
def pipeline_meta_dir():
    return join(dirname(__file__), 'functional', 'export_pipeline', 'data')


@fixture
def last_pipeline_step(pipeline_meta_dir):
    return join(pipeline_meta_dir, 'mlvtools_step5_sort_data.dvc')


@fixture
def expected_export_pipeline(pipeline_meta_dir):
    return join(pipeline_meta_dir, 'exported_pipeline.sh')


@fixture
def ordered_pipeline_steps(pipeline_meta_dir):
    return [join(pipeline_meta_dir, step) for step in ('mlvtools_step1_sanitize_data.dvc',
                                                       'mlvtools_step2_split_data.dvc',
                                                       'mlvtools_step3_convert_binaries.dvc',
                                                       'mlvtools_step4_convert_octals.dvc',
                                                       'mlvtools_step5_sort_data.dvc')]
