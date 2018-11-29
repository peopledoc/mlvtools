from os.path import realpath, dirname, join, exists

from mlvtools.export_pipeline import export_pipeline
from tests.helpers.utils import write_dvc_file

CURRENT_DIR = realpath(dirname(__file__))


def test_should_export_pipeline(work_dir, mocker):
    """
        Test pipeline is extracted and commands are written to be called in the right order.
        Other files are ignored.
    """

    cmd1 = './cmd1.py -i ../in.csv -f --out ./toto.csv'
    write_dvc_file(join(work_dir, 'step1.dvc'), cmd1, deps=['../in.csv'],
                   outs=['../toto.csv'])
    cmd2 = './cmd2.py -i ../toto.csv --out ./metrics.csv -o2 p.kl'
    write_dvc_file(join(work_dir, 'step2.dvc'), cmd2,
                   deps=['../toto.csv'], outs=['./metrics.csv', 'p.kl'])
    target_step = join(work_dir, 'step3.dvc')
    cmd3 = './cmd3.py -m ./metrics.csv'
    write_dvc_file(target_step, cmd3, deps=['./metrics.csv'], outs=['./res'])

    # Add Noise
    cmd_noise = './cmd0.py -o ../in.csv'
    write_dvc_file(join(work_dir, 'noise_file'), cmd_noise, deps=[''], outs=['../in.csv'])

    output_script = join(work_dir, 'exported_pipeline.sh')
    export_pipeline(target_step, output_script, work_dir)

    assert exists(output_script)
    with open(output_script, 'r') as fd:
        script_content = fd.readlines()

    assert [cmd.strip('\n') for cmd in script_content if cmd.startswith('./cmd')] == [cmd1, cmd2, cmd3]
    assert cmd_noise not in script_content
