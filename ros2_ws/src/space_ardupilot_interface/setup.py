from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'space_ardupilot_interface'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['README.md']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    tests_require=['pytest'],
    zip_safe=True,
    maintainer='space team',
    maintainer_email='todo@example.com',
    description='ArduPilot Rover ROS 2 adapter for velocity command translation.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'ardupilot_adapter = space_ardupilot_interface.ardupilot_adapter:main',
            'extnav_publisher = space_ardupilot_interface.extnav_publisher:main',
        ],
    },
)
