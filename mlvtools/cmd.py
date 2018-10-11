import logging
from argparse import ArgumentParser
from typing import Tuple, Any

from mlvtools.exception import MlVToolException


class CommandHelper:
    def run_cmd(self, *args, **kwargs):
        try:
            self.run(*args, **kwargs)
        except MlVToolException as e:
            logging.critical(e)
        except Exception as e:
            logging.critical(f'Unexpected error happened: {e}')

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

    def parse(self, args: Tuple[Any] = None):
        # Args must be explicitly None if they are empty
        return self.parser.parse_args(args=args if args else None)
