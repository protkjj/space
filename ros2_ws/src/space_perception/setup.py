from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'space_perception'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    tests_require=['pytest'],
    zip_safe=True,
    maintainer='space team',
    maintainer_email='todo@example.com',
    description='RGB-D perception helpers for teleoperation and mission sensing.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'depth_overlay_node = space_perception.depth_overlay_node:main',
            (
                'terrain_pointcloud_filter_node = '
                'space_perception.terrain_pointcloud_filter_node:main'
            ),
            (
                'local_elevation_map_node = '
                'space_perception.local_elevation_map_node:main'
            ),
            (
                'terrain_feature_node = '
                'space_perception.terrain_feature_node:main'
            ),
            (
                'terrain_traversability_node = '
                'space_perception.terrain_traversability_node:main'
            ),
            (
                'traversability_calibration = '
                'space_perception.traversability_calibration:main'
            ),
        ],
    },
)
