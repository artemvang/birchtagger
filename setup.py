#!/usr/bin/env python
from setuptools import setup, find_packages

requirements = [
    "numpy==1.14.0",
    "scipy==1.0.0",
    "PyStemmer==1.3.0",
    "xxhash==1.0.1",
]

setup(
    name="birchnlp",
    version="0.1.0",
    description="NLP swiss army knife for russian language",
    install_requires=requirements,
    packages=find_packages('.', exclude='tests'),
    include_package_data=True,
)
