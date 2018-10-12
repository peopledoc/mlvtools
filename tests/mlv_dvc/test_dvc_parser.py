from os.path import join, basename

import pytest
from pytest import fixture
from yaml import YAMLError

from mlvtools.exception import MlVToolException
from mlvtools.mlv_dvc.dvc_parser import get_dvc_dependencies, get_dvc_meta, DvcMeta
from tests.helpers.utils import write_dvc_file


@fixture
def base_steps(work_dir):
    steps = [join(work_dir, 'step1.yml'), join(work_dir, 'step2.yml'), join(work_dir, 'step3.yml'),
             join(work_dir, 'step4.yml'), join(work_dir, 'step5.yml')]

    write_dvc_file(steps[0], 'cmd1', deps=['./pipeline_in'], outs=['./s1_out'])
    write_dvc_file(steps[1], 'cmd2', deps=['./s1_out'], outs=['./s2_out'])
    write_dvc_file(steps[2], 'cmd3', deps=['./s2_out'], outs=['./s3_out'])
    write_dvc_file(steps[3], 'cmd4', deps=['./s2_out'], outs=['./s4_out'])
    write_dvc_file(steps[4], 'cmd5', deps=['./s3_out', './s4_out'], outs=['./s5_out'])
    return steps


def test_should_get_dependencies_steps(base_steps):
    """
        Test all steps to in denpendency of the target step

             +-----------+              +---------------+
             | step1.dvc |              | isolated1.dvc |
             +-----------+              +---------------+
                    *
             +-----------+              +---------------+
             | step2.dvc |              | isolated2.dvc |
             +-----------+              +---------------+
         **                  **
+-----------+             +-----------+
| step3.dvc |             | step4.dvc |
+-----------+             +-----------+
                **    **
             +-----------+
             | step5.dvc |
             +-----------+
    """

    dependencies = list(get_dvc_dependencies(target_file_path=base_steps[-1], dvc_files=base_steps))
    # Topological sort solution can be 1 -> 2 -> 3 -> 4 -> 5
    #                               or 1 -> 2 -> 4 -> 3 -> 5
    expected_steps = ([basename(base_steps[idx]) for idx in (0, 1, 2, 3, 4)],
                      [basename(base_steps[idx]) for idx in (0, 1, 3, 2, 4)]
                      )

    assert [d.name for d in dependencies] in expected_steps


def test_should_remove_not_targeted_steps(work_dir, base_steps):
    """
        Test get dependencies but does not include steps not directly in dependencies
             +-----------+
             | step1.dvc |
             +-----------+**
                    *       **********
             +-----------+           +---------------+
             | step2.dvc |           | step2_bis.dvc |
             +-----------+           +---------------+
         **                  **
+-----------+             +-----------+
| step3.dvc |             | step4.dvc |
+-----------+             +-----------+
                **    **            **
             +-----------+            +-----------+
             | step5.dvc |            | step6.dvc |
             +-----------+            +-----------+
    """

    target_step = join(work_dir, 'step6.dvc')
    base_steps += [join(work_dir, 'step2_bis.dvc'), target_step]

    write_dvc_file(base_steps[-2], 'cmd2_bis', deps=['./s1_out'], outs=['./s2_bis_out'])
    write_dvc_file(base_steps[-1], 'cmd6', deps=['./s4_out'], outs=['./s6_out'])

    expected_steps = [base_steps[0], base_steps[1], base_steps[3], target_step]
    dependencies = list(get_dvc_dependencies(target_file_path=target_step, dvc_files=base_steps))
    # Topological solution is 1 -> 2 -> 4 -> 6
    assert [d.name for d in dependencies] == [basename(s) for s in expected_steps]


def test_should_raise_if_target_does_not_exist(base_steps):
    """
        Test raises if target step does not exist
    """
    with pytest.raises(MlVToolException) as ex:
        get_dvc_dependencies(target_file_path='does_not_exit.dvc', dvc_files=base_steps)
    assert isinstance(ex.value.__cause__, IOError)


def test_should_raise_if_target_format_error(work_dir, base_steps):
    """
        Test raises if target format error
    """
    target = join(work_dir, 'format_error.dvc')
    with open(target, 'wb') as fd:
        fd.write(b'k:v:\n\t\t-')

    with pytest.raises(MlVToolException) as ex:
        get_dvc_dependencies(target_file_path=target, dvc_files=base_steps)
    assert isinstance(ex.value.__cause__, YAMLError)


def test_should_raise_dvc_file_step_not_found(base_steps):
    """
        Test raises if dvc file step not found
    """
    base_steps.append('./does_not_exist_step.dvc')
    with pytest.raises(MlVToolException) as ex:
        get_dvc_dependencies(target_file_path=base_steps[0], dvc_files=base_steps)
    assert isinstance(ex.value.__cause__, IOError)


def test_should_raise_dvc_file_step_format_error(base_steps, work_dir):
    """
        Test raises if dvc file step format error
    """
    target = join(work_dir, 'format_error.dvc')
    with open(target, 'wb') as fd:
        fd.write(b'k:v:\n\t\t-')
    base_steps.append(target)

    with pytest.raises(MlVToolException) as ex:
        get_dvc_dependencies(target_file_path=base_steps[0], dvc_files=base_steps)
    assert isinstance(ex.value.__cause__, YAMLError)


def test_should_get_dvc_meta(work_dir):
    """
        Test get DVC Meta from a DVC meta file
    """
    cmd = 'step_cmd -p toto --param2 ./param2'
    deps = ['./input1.tx', './data/in2.csv']
    outs = ['./out1.csv', '../../out2.csv']
    step_file = join(work_dir, 'step_test.dvc')
    write_dvc_file(step_file, cmd, deps, outs)

    dvc_meta = get_dvc_meta(step_file)
    assert dvc_meta == DvcMeta(name='step_test.dvc', cmd=cmd, deps=deps, outs=outs)


def test_should_raise_if_not_exists():
    """
        Test get dvc meta from a dvc file raise if does not exist
    """
    with pytest.raises(MlVToolException) as ex:
        get_dvc_meta('./does_not_exits.dvc')
    assert isinstance(ex.value.__cause__, IOError)


def test_should_raise_if_bad_format(work_dir):
    """
        Test get dvc meta from a dvc file raise if bad format
    """
    target = join(work_dir, 'format_error.dvc')
    with open(target, 'wb') as fd:
        fd.write(b'k:v:\n\t\t-')

    with pytest.raises(MlVToolException) as ex:
        get_dvc_meta(target)
    assert isinstance(ex.value.__cause__, YAMLError)


def test_should_raise_if_content_error(work_dir):
    """
        Test get dvc meta from a dvc file raise if content error
    """
    target = join(work_dir, 'wrong_content.dvc')
    with open(target, 'w') as fd:
        fd.write('test')

    with pytest.raises(MlVToolException) as ex:
        get_dvc_meta(target)
    assert isinstance(ex.value.__cause__, AttributeError)
