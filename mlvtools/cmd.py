import logging
import traceback
from os.path import exists

import argparse
from argparse import ArgumentParser, Namespace
from typing import Tuple, Any, List

from mlvtools.conf.conf import get_work_directory, get_conf_file_default_path, load_conf_or_default, MlVToolConf
from mlvtools.exception import MlVToolException
from mlvtools.helper import to_sanitized_path


class SanitizePath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, to_sanitized_path(values))


class CommandHelper:
    def set_log_level(self, args: Namespace):
        logging.addLevelName(logging.WARNING + 1, 'MLV-tools')
        log_format = '%(levelname).8s:%(message)s'
        if args.debug:
            logging.basicConfig(level=logging.DEBUG, format=log_format)
        elif args.verbose:
            logging.basicConfig(level=logging.INFO, format=log_format)

    def check_force(self, force: bool, outputs: List[str]):
        if force:
            return
        for output in outputs:
            if exists(output):
                raise MlVToolException(f'Output file {output} already exists, '
                                       f'use --force option to overwrite it')

    def get_conf(self, working_dir_param: str, input_file_arg: str, conf_path_arg: str) -> MlVToolConf:
        work_directory = working_dir_param or get_work_directory(input_file_arg)
        conf_path = conf_path_arg or get_conf_file_default_path(work_directory)
        return load_conf_or_default(conf_path, work_directory)

    def run_cmd(self, *args, **kwargs):
        try:
            self.run(*args, **kwargs)
        except MlVToolException as e:
            logging.critical(e)
            logging.debug(traceback.format_exc())
        except Exception as e:
            logging.critical(f'Unexpected error happened: {e}')
            logging.info('Reason: ', exc_info=True)

    def run(self, *args, **kwargs):
        raise NotImplementedError()


class ArgumentBuilder:
    def __init__(self, **kwargs):
        self.parser = ArgumentParser(**kwargs)

    def add_work_dir_argument(self) -> 'ArgumentBuilder':
        self.parser.add_argument('-w', '--working-directory', type=str,
                                 help='Working directory. Relative path are calculated from it. '
                                      'Default value is the top directory')
        return self

    def add_conf_path_argument(self) -> 'ArgumentBuilder':
        self.parser.add_argument('-c', '--conf-path', type=str,
                                 help='Path to configuration file. By default it '
                                      'takes [git_top_dir]/.mlvtools using git rev-parse')
        return self

    def add_force_argument(self) -> 'ArgumentBuilder':
        self.parser.add_argument('-f', '--force', action='store_true',
                                 help='Force output overwrite.')
        return self

    def add_docstring_conf(self) -> 'ArgumentBuilder':
        self.parser.add_argument('--docstring-conf', type=str,
                                 help='User configuration used for docstring templating')
        return self

    def add_argument(self, *args, **kwargs) -> 'ArgumentBuilder':
        self.parser.add_argument(*args, **kwargs)
        return self

    def add_path_argument(self, *args, **kwargs) -> 'ArgumentBuilder':
        self.parser.add_argument(*args, **kwargs, action=SanitizePath)
        return self

    def parse(self, args: Tuple[Any] = None):
        self.parser.add_argument('-v', '--verbose', action='store_true',
                                 help='Increase the log level to INFO')
        self.parser.add_argument('--debug', action='store_true',
                                 help='Increase the log level to DEBUG')

        # Args must be explicitly None if they are empty
        return self.parser.parse_args(args=args if args else None)
