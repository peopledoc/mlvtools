#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python packaging."""
import glob
import os
from os.path import join
from typing import List

from setuptools import setup, find_packages

#: Absolute path to directory containing setup.py file.
current_dir = os.path.abspath(os.path.dirname(__file__))

readme = open(join(current_dir, 'README.md')).read()
version = '0.0.1'
requirements = []
with open(join(current_dir, 'requirements.txt'), 'r') as fd:
    for line in fd.readlines():
        requirements.append(line)


def extract_scripts(root_dir: str) -> List[str]:
    return glob.glob(join(root_dir, '*'))


def get_packages(path: str):
    return [join(path, p) for p in find_packages(join(path))]


if __name__ == '__main__':  # Do not run setup() when we import this module.
    print('--------------------')
    print(get_packages('./src'))
    print(extract_scripts('./cmd'))
    print('--------------------')

    setup(
        name='ml-versionning-tools',
        version=version,
        description='Set of Machine Learning versioning helpers',
        long_description=readme,
        classifiers=[
            "Programming Language :: Python :: 3",
        ],
        keywords='peopledoc',
        author='Peopledoc',
        author_email='stephanie.bracaloni@people-doc.com',
        url='http://github.com/peopledoc/ml-versionning-tools',
        packages=['mlvtool'],
        include_package_data=True,
        zip_safe=True,
        scripts=extract_scripts('./cmd'),
        install_requires=requirements
    )
