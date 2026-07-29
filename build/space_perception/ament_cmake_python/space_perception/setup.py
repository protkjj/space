from setuptools import find_packages
from setuptools import setup

setup(
    name='space_perception',
    version='0.1.0',
    packages=find_packages(
        include=('space_perception', 'space_perception.*')),
)
