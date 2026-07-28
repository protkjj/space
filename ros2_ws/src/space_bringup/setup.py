from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'space_bringup'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config', 'common'), glob('config/common/*')),
        (os.path.join('share', package_name, 'config', 'navigation'), glob('config/navigation/*')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    tests_require=['pytest'],
    zip_safe=True,
    maintainer='space team',
    maintainer_email='todo@example.com',
    description='Simulation and non-actuating hardware orchestration.',
    license='MIT',
    entry_points={'console_scripts': []},
)
