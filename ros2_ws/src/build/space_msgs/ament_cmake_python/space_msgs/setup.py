from setuptools import find_packages
from setuptools import setup

setup(
    name='space_msgs',
    version='0.1.0',
    packages=find_packages(
        include=('space_msgs', 'space_msgs.*')),
)
