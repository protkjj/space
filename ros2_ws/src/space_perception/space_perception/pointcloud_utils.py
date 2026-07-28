"""Point-cloud and transform helpers shared by terrain ROS nodes."""

import numpy as np
from sensor_msgs.msg import PointField
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header


XYZ_FIELDS = [
    PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
    PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
    PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
]

ELEVATION_FIELDS = [
    *XYZ_FIELDS,
    PointField(
        name='variance', offset=12, datatype=PointField.FLOAT32, count=1
    ),
    PointField(
        name='point_count', offset=16, datatype=PointField.UINT32, count=1
    ),
]

ELEVATION_DTYPE = np.dtype(
    [
        ('x', '<f4'),
        ('y', '<f4'),
        ('z', '<f4'),
        ('variance', '<f4'),
        ('point_count', '<u4'),
    ]
)


def cloud_xyz_numpy(message) -> np.ndarray:
    """Read XYZ fields into an unorganized float64 Nx3 array."""
    points = point_cloud2.read_points_numpy(
        message,
        field_names=['x', 'y', 'z'],
        skip_nans=False,
    )
    return np.asarray(points, dtype=np.float64).reshape((-1, 3))


def create_xyz_cloud(header: Header, points: np.ndarray):
    """Create an XYZ float32 PointCloud2 without per-point Python objects."""
    return point_cloud2.create_cloud(
        header, XYZ_FIELDS, np.asarray(points, dtype=np.float32)
    )


def create_elevation_cloud(header: Header, rows: np.ndarray):
    """Create x,y,z,variance,point_count PointCloud2 from numeric rows."""
    rows = np.asarray(rows).reshape((-1, 5))
    structured = np.empty(len(rows), dtype=ELEVATION_DTYPE)
    for index, name in enumerate(ELEVATION_DTYPE.names):
        structured[name] = rows[:, index]
    return point_cloud2.create_cloud(
        header, ELEVATION_FIELDS, structured, point_step=20
    )


def transform_to_matrix(transform) -> np.ndarray:
    """Convert geometry_msgs Transform to a 4x4 NumPy matrix."""
    translation = transform.translation
    rotation = transform.rotation
    x, y, z, w = rotation.x, rotation.y, rotation.z, rotation.w
    norm = x * x + y * y + z * z + w * w
    if norm == 0.0:
        raise ValueError('transform quaternion has zero norm')
    scale = 2.0 / norm
    matrix = np.eye(4, dtype=np.float64)
    matrix[:3, :3] = [
        [1.0 - scale * (y * y + z * z), scale * (x * y - z * w),
         scale * (x * z + y * w)],
        [scale * (x * y + z * w), 1.0 - scale * (x * x + z * z),
         scale * (y * z - x * w)],
        [scale * (x * z - y * w), scale * (y * z + x * w),
         1.0 - scale * (x * x + y * y)],
    ]
    matrix[:3, 3] = [translation.x, translation.y, translation.z]
    return matrix
