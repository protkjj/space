from setuptools import find_packages, setup

package_name = 'space_controller'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    tests_require=['pytest'],
    zip_safe=True,
    maintainer='space team',
    maintainer_email='todo@example.com',
    description='Backend-neutral command clipping, mode gate, and watchdog.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'command_safety_node = space_controller.command_safety:main',
        ],
    },
)
