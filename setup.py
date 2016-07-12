#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "argparse"
]

test_requirements = [
    "argparse",
    "mock"
]

setup(
    name='etphantomutil',
    version='0.1.0',
    description="A set of utilities to run Etphantom from the command line",
    long_description=readme + '\n\n' + history,
    author="Christopher Churas",
    author_email='churas@ncmir.ucsd.edu',
    url='https://github.com/coleslaw481/etphantomutil',
    packages=[
        'etphantomutil',
    ],
    package_dir={'etphantomutil':
                 'etphantomutil'},
    scripts = ['etphantomutil/rotate_3dmarkers.py',
               'etphantomutil/shift_fidfilemarkers.py',
               'etphantomutil/create_tiltseries.py'],
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='etphantomutil',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
