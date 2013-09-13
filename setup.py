#!/usr/bin/env python
# encoding: utf-8

# fix for TypeError: 'NoneType' object is not callable
import multiprocessing  # noqa

from setuptools import setup
import pkg_resources
version = pkg_resources.require("fastbill")[0].version

setup(
    name='fastbill',
    version=version,
    description='A thin python wrapper for the fastbill API',
    long_description=open('README.md', 'r').read(),
    author='Dimitar Roustchev',
    author_email='dimitar.roustchev@stylight.com',
    url='http://github.com/stylight/python-fastbill',
    license='MIT License',
    packages=['fastbill'],
    install_requires=[
        'requests==0.14.2',
    ],
    setup_requires=["nose>=1.0", "httpretty==0.6.3"],
    test_suite="nose.collector",
    keywords='fastbill api'
)
