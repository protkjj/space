from setuptools import find_packages, setup

package_name = 'space_perception'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='space team',
    maintainer_email='todo@example.com',
    description='RGB-D perception helpers for teleoperation and mission sensing.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'depth_overlay_node = space_perception.depth_overlay_node:main',
        ],
    },
)
