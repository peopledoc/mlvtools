#!/usr/bin/env python3
import argparse
import glob
import logging
import sys
from os.path import join, basename, exists

from mlvtools.cmd import CommandHelper, ArgumentBuilder
from mlvtools.conf.conf import MlVToolConf, get_script_output_path
from mlvtools.diff.parse import get_ast, get_ast_from_file, is_ast_equal
from mlvtools.exception import MlVToolException
from mlvtools.ipynb_to_python import get_converted_script


def compare(notebook_path: str, script_path: str, conf: MlVToolConf) -> bool:
    """
        Compare the script obtained by notebook conversion using ipynb_to_python
        with the actual script.
    """
    generated_script = get_converted_script(notebook_path, conf)
    generated_ast = get_ast(generated_script, name=notebook_path)

    script_ast = get_ast_from_file(script_path)

    return is_ast_equal(generated_ast, script_ast)


def run_consistency_check(notebook_path: str, script_path: str, conf: MlVToolConf) -> bool:
    """
        Call comparison on notebook and script then display the result.
    """
    logging.info(f'Run consistency check on ({notebook_path}, {script_path})')

    if not exists(script_path):
        logging.error(f'Script path {script_path} does not exists.')
        return False

    equals = compare(notebook_path, script_path, conf)
    if equals:
        logging.log(logging.WARNING + 1, f'Script content is the same for {basename(notebook_path)} '
                                         f'and {basename(script_path)}')
    else:
        logging.error(f'Difference found between {notebook_path} and {script_path}.'
                      f'Ensure notebook conversion is up to date (ipynb_to_python)')
    return equals


class IPynbCheckScript(CommandHelper):

    def run(self, *args, **kwargs):
        args = ArgumentBuilder(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                               description='Checks notebook and script consistency') \
            .add_work_dir_argument() \
            .add_conf_path_argument() \
            .add_path_argument('-n', '--notebook', type=str, help='The notebook to check') \
            .add_path_argument('-s', '--script', required=True, type=str, help='The script to check') \
            .parse(args)

        self.set_log_level(args)

        conf = self.get_conf(args.working_directory, args.notebook, args.conf_path)

        equals = run_consistency_check(args.notebook, args.script, conf)
        sys.exit(0 if equals else 1)


class IPynbCheckAllScripts(CommandHelper):
    def run(self, *args, **kwargs):
        args = ArgumentBuilder(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                               description='Checks all notebooks and scripts consistency.\n'
                                           'Run the up to date checks on all notebooks from the notebook directory. '
                                           'Script names are deduce from the conf.') \
            .add_work_dir_argument() \
            .add_conf_path_argument() \
            .add_path_argument('-n', '--notebooks-dir', type=str, help='Notebooks directory') \
            .add_argument('-i', '--ignore', action='append', help='Notebook filename to ignore', default=[]) \
            .parse(args)

        self.set_log_level(args)
        conf = self.get_conf(args.working_directory, args.notebooks_dir, args.conf_path)
        if not conf.path:
            raise MlVToolException('Configuration file is mandatory')

        equals = True
        for notebook in glob.glob(join(args.notebooks_dir, '*.ipynb')):
            if basename(notebook) in args.ignore:
                logging.info(f'Ignore notebook {notebook}')
                continue

            associated_script = get_script_output_path(notebook, conf)
            equals = run_consistency_check(notebook, associated_script, conf) and equals
        sys.exit(0 if equals else 1)
