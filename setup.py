#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python packaging."""
import glob
from os.path import join, abspath, dirname
from typing import List

from setuptools import setup, find_packages

#: Absolute path to directory containing setup.py file.
current_dir = abspath(dirname(__file__))

with open(join(current_dir, 'README.md')) as fd:
    readme = fd.read()

with open(join(current_dir, 'requirements', 'requirements.txt'), 'r') as fd:
    requirements = fd.readlines()

with open(join(current_dir, 'requirements', 'dev_requirements.txt'), 'r') as fd:
    dev_requirements = fd.readlines()

with open(join(current_dir, 'VERSION'), 'r') as fd:
    version = fd.read()


def extract_scripts(root_dir: str) -> List[str]:
    return glob.glob(join(root_dir, '*'))


def get_packages(path: str):
    return [join(path, p) for p in find_packages(join(path))]


if __name__ == '__main__':  # Do not run setup() when we import this module.
    setup(
        name='ml-versioning-tools',
        version=version,
        description='Set of Machine Learning versioning helpers',
        long_description=readme,
        long_description_content_type='text/markdown',
        classifiers=[
            "Operating System :: POSIX",
            "Programming Language :: Python :: 3",
        ],
        python_requires='>=3.6',
        keywords='peopledoc',
        author='Peopledoc',
        author_email='stephanie.bracaloni@people-doc.com',
        url='http://github.com/peopledoc/ml-versionning-tools',
        packages=['mlvtools'],
        include_package_data=True,
        zip_safe=True,
        scripts=extract_scripts('./cmd'),
        install_requires=requirements,
        extras_require={
            'dev': dev_requirements
        }
    )
