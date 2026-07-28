from setuptools import find_packages, setup

package_name = 'space_px4_interface'

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
    description='Optional PX4 uORB to ROS 2 topic bridge skeleton for the rover.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'px4_bridge = space_px4_interface.px4_bridge:main',
        ],
    },
)
