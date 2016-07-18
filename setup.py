#!/usr/bin/env python
# encoding: utf-8

# fix for TypeError: 'NoneType' object is not callable
import multiprocessing  # noqa

from setuptools import setup

try:
    from os.path import abspath, dirname, join
    _desc = join(dirname(abspath(__file__)), 'README.rst')
    long_description = open(_desc, 'r').read()
except IOError:
    long_description = "fastbill"


setup(
    name='fastbill',
    version="0.7.2",  # Don't forget to update fastbill.version too
    description='A thin python wrapper for the fastbill API',
    long_description=long_description,
    author='python-fastbill contributors',
    author_email='busdev_engineers@stylight.com',
    url='http://github.com/stylight/python-fastbill',
    license='MIT License',
    packages=['fastbill'],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Financial',
        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'requests',
        'six'
    ],
    setup_requires=["nose>=1.0", "httpretty==0.8.10", 'mock==1.0.1'],
    test_suite="nose.collector",
    keywords='fastbill api'
)
