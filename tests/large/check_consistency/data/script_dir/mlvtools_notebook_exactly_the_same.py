#!/usr/bin/env python3
# Generated from ./notebooks/notebook_exactly_the_same.ipynb
import argparse


def mlvtools_notebook_exactly_the_same(year):
    """
    :param str year: your age
    """

    # A notebook about age

    # This is a comment
    print(f'hello ! Your are {age} years old!!!')

    # A Tag
    print('This is the end')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command for script mlvtools_notebook_exactly_the_same')

    parser.add_argument('--year', type=str, required=True, help="your age")

    args = parser.parse_args()

    mlvtools_notebook_exactly_the_same(args.year)
