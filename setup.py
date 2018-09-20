#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python packaging."""
import glob
from os.path import join, abspath, dirname
from typing import List

from setuptools import setup

#: Absolute path to directory containing setup.py file.
current_dir = abspath(dirname(__file__))


def extract_scripts(root_dir: str) -> List[str]:
    return glob.glob(join(root_dir, '*'))


if __name__ == '__main__':  # Do not run setup() when we import this module.
    setup(scripts=extract_scripts('./cmd'))
