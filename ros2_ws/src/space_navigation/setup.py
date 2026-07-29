from glob import glob
import os

from setuptools import find_packages, setup


package_name = 'space_navigation'

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
    description='Point-and-click autonomous navigation for the space rover.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'goal_navigator = space_navigation.goal_navigator:main',
            'send_goal = space_navigation.send_goal:main',
        ],
    },
)
