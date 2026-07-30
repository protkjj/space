import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/kj/Desktop/space/ros2_ws/src/space_bringup/install/space_bringup'
