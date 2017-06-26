#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from distutils.core import setup

setup(
    name='aiolifxc',
    packages=['aiolifxc'],
    version='0.5.0',
    author='Brian May',
    author_email='brian@linuxpenguins.xyz',
    description='API for local communication with LIFX devices '
                'over a LAN with asyncio.',
    url='http://github.com/brianmay/aiolifx',
    keywords=['lifx', 'light', 'automation'],
    license='MIT',
    install_requires=[
        "bitstring",
    ],
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ])
