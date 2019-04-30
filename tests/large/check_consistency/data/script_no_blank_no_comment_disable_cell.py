#!/usr/bin/env python3
from typing import List
import argparse
def mlvtools_notebook_blank_and_comment_diff(name: str):
    """
    :param str name: your name
    """
    print(f'hello {name}')
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command for script mlvtools_notebook_blank_and_comment_diff')
    parser.add_argument('--name', type=str,
        required=True, help="your name")
    args = parser.parse_args()
    mlvtools_notebook_blank_and_comment_diff(args.name)