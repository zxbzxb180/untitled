#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name='udev_sso_server',
    version='0.2.4',
    url='',
    description='udev sso server. only support cas',
    author='xtz',
    author_email='xutaozhe@126.com',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.6",
    zip_safe=False,
    classifiers=[
        'Private :: Do Not Upload'
    ]
)
