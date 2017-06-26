#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "bitstring",
]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest',
]

setup(
    name='aiolifxc',
    version='0.5.1',
    description='API for local communication with LIFX devices '
                'over a LAN with asyncio.',
    long_description=readme + '\n\n' + history,
    author="Brian May",
    author_email='brian@linuxpenguins.xyz',
    url='http://github.com/brianmay/aiolifx',
    packages=find_packages(include=['aiolifxc']),
    include_package_data=True,
    install_requires=requirements,
    license='MIT',
    keywords=['lifx', 'light', 'automation'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
