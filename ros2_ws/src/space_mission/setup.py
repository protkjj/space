from glob import glob
import os

from setuptools import find_packages, setup


package_name = 'space_mission'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        ('share/' + package_name, ['package.xml']),
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.yaml'),
        ),
    ],
    install_requires=['setuptools'],
    tests_require=['pytest'],
    zip_safe=True,
    maintainer='space team',
    maintainer_email='todo@example.com',
    description='Mission-level traversability fusion and orchestration.',
    license='MIT',
    entry_points={
        'console_scripts': [
            (
                'traversability_fusion_node = '
                'space_mission.traversability_fusion_node:main'
            ),
        ],
    },
)
