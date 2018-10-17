#!/usr/bin/env python3
import argparse
import glob
import logging
from collections import namedtuple
from os.path import abspath, join, exists
from os.path import realpath, dirname
from typing import List

from mlvtools.cmd import CommandHelper, ArgumentBuilder
from mlvtools.exception import MlVToolException
from mlvtools.helper import get_git_top_dir, write_template
from mlvtools.mlv_dvc.dvc_parser import get_dvc_dependencies

ARG_IDENTIFIER = '-'

logging.getLogger().setLevel(logging.INFO)
CURRENT_DIR = realpath(dirname(__file__))

PIPELINE_EXPORT_TEMPLATE_NAME = 'pipeline-export.tpl'
ConfigurableCmds = namedtuple('ConfigurableCmds', ('cmds', 'variables'))


def get_dvc_files(dvc_target_file: str) -> List[str]:
    """
        Return the list of potential DVC meta file pipeline step.
        DVC meta files are all located in the same directory for a given pipeline.
        DVC file extension: .dvc
    """
    if not exists(dvc_target_file):
        raise MlVToolException(f'Targeted pipeline metadata step {dvc_target_file} does not exist')
    return glob.glob(join(dirname(dvc_target_file), '*.dvc'))


def export_pipeline(dvc_meta_file: str, output: str, work_dir: str):
    """
     Generate an executable script to run a whole pipeline
    """

    ordered_dvc_metas = get_dvc_dependencies(dvc_meta_file, get_dvc_files(dvc_meta_file))

    template_data = {'work_dir': work_dir, 'cmds': [dvc_meta.cmd for dvc_meta in ordered_dvc_metas]}

    template_path = join(CURRENT_DIR, '..', 'template', PIPELINE_EXPORT_TEMPLATE_NAME)
    write_template(output, template_path, info=template_data)


class MlExportPipeline(CommandHelper):
    def run(self, *args, **kwargs):
        args = ArgumentBuilder(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                               description='Export a DVC pipeline to sequential execution.') \
            .add_force_argument() \
            .add_work_dir_argument() \
            .add_argument('--dvc', type=str, required=True, help='DVC targeted pipeline metadata step') \
            .add_argument('-o', '--output', type=str, help='The Python pipeline script output path',
                          required=True) \
            .parse(args)

        work_dir = args.working_directory or get_git_top_dir(dirname(args.dvc))

        if not args.force and exists(args.output):
            raise MlVToolException(f'Output file {args.output} already exists, use --force option to overwrite it')

        export_pipeline(args.dvc, args.output, work_dir)

        logging.info(f'Pipeline is exported in {abspath(args.output)}.')
