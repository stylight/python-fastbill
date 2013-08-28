#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages

import fastbill
version = str(fastbill.__version__)

setup(
    name='fastbill',
    version=version,
    description='A thin python wrapper for the fastbill API',
    #TODO: write README.txt
    #long_description=open('./README.txt', 'r').read(),
    author='Dimitar Roustchev',
    author_email='dimitar.roustchev@stylight.com',
    url='http://github.com/stylight/stylight-fastbill',
    #TODO: Verify license
    license='MIT License',
    packages=find_packages(),
    install_requires=[
        'requests==0.14.2'
    ],
    test_requires=[
        'nose==1.3.0'
    ],
    keywords='fastbill api'
)
