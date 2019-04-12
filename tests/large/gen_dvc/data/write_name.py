#!/usr/bin/env python3
import argparse
from os.path import exists, join, dirname


def mlvtools_write_hello_in_file(output_file: str, name: str):
    """
    :param str output_file: path to the output file
    :param str name: your name
    :dvc-out output_file: {{conf.output_file}}
    :dvc-extra: --name {{conf.name}}
    """
    marker_path = join(dirname(output_file), 'ran.once')
    first_run = not exists(marker_path)
    if first_run:
        with open(marker_path, 'w') as fd:
            fd.write(' ')

    with open(output_file, 'w') as fd:
        suffix = 'First run' if first_run else 'Not the first run'
        fd.write(f'Hello {name}! {suffix}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command for script mlvtools_write_hello_in_file')
    parser.add_argument('--output-file', type=str,
                        required=True, help="path to the output file")
    parser.add_argument('--name', type=str,
                        required=True, help="your name")
    args = parser.parse_args()

    mlvtools_write_hello_in_file(args.output_file, args.name)
