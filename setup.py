#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages

import fastbill
version = str(fastbill.__version__)

setup(
    name='fastbill',
    version=version,
    author='Dimitar Roustchev',
    author_email='dimitar.roustchev@stylight.com',
    url='http://github.com/stylight/stylight-fastbill',
    description='python wrapper for Fastbill',
    #TODO: write README.txt
    #long_description=open('./README.txt', 'r').read(),
    packages=find_packages(),
    install_requires=[
        'requests>=1.2.3'
    ],
    #TODO: Verify license
    license='MIT License',
    keywords='fastbill api'
)
