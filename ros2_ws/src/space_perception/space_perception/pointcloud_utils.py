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

FEATURE_FIELDS = [
    *XYZ_FIELDS,
    PointField(name='slope', offset=12, datatype=PointField.FLOAT32, count=1),
    PointField(
        name='roughness', offset=16, datatype=PointField.FLOAT32, count=1
    ),
    PointField(
        name='step_height', offset=20, datatype=PointField.FLOAT32, count=1
    ),
    PointField(
        name='elevation_variance',
        offset=24,
        datatype=PointField.FLOAT32,
        count=1,
    ),
    PointField(
        name='point_count', offset=28, datatype=PointField.UINT32, count=1
    ),
    PointField(
        name='neighbor_count', offset=32, datatype=PointField.UINT32, count=1
    ),
    PointField(
        name='neighborhood_coverage',
        offset=36,
        datatype=PointField.FLOAT32,
        count=1,
    ),
    PointField(
        name='confidence', offset=40, datatype=PointField.FLOAT32, count=1
    ),
]

FEATURE_DTYPE = np.dtype(
    [
        ('x', '<f4'),
        ('y', '<f4'),
        ('z', '<f4'),
        ('slope', '<f4'),
        ('roughness', '<f4'),
        ('step_height', '<f4'),
        ('elevation_variance', '<f4'),
        ('point_count', '<u4'),
        ('neighbor_count', '<u4'),
        ('neighborhood_coverage', '<f4'),
        ('confidence', '<f4'),
    ]
)

TRAVERSABILITY_FIELDS = [
    *XYZ_FIELDS,
    PointField(
        name='traversability', offset=12, datatype=PointField.FLOAT32, count=1
    ),
    PointField(
        name='slope_penalty', offset=16, datatype=PointField.FLOAT32, count=1
    ),
    PointField(
        name='roughness_penalty',
        offset=20,
        datatype=PointField.FLOAT32,
        count=1,
    ),
    PointField(
        name='step_penalty', offset=24, datatype=PointField.FLOAT32, count=1
    ),
    PointField(
        name='uncertainty_penalty',
        offset=28,
        datatype=PointField.FLOAT32,
        count=1,
    ),
    PointField(
        name='confidence', offset=32, datatype=PointField.FLOAT32, count=1
    ),
    PointField(name='valid', offset=36, datatype=PointField.UINT8, count=1),
    PointField(
        name='limiting_factor', offset=37, datatype=PointField.UINT8, count=1
    ),
]

TRAVERSABILITY_DTYPE = np.dtype(
    [
        ('x', '<f4'),
        ('y', '<f4'),
        ('z', '<f4'),
        ('traversability', '<f4'),
        ('slope_penalty', '<f4'),
        ('roughness_penalty', '<f4'),
        ('step_penalty', '<f4'),
        ('uncertainty_penalty', '<f4'),
        ('confidence', '<f4'),
        ('valid', 'u1'),
        ('limiting_factor', 'u1'),
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


def elevation_cloud_numpy(message) -> np.ndarray:
    """Validate and unpack mixed-type elevation fields into float64 rows."""
    expected = {
        'x': PointField.FLOAT32,
        'y': PointField.FLOAT32,
        'z': PointField.FLOAT32,
        'variance': PointField.FLOAT32,
        'point_count': PointField.UINT32,
    }
    actual = {
        field.name: field
        for field in message.fields
        if field.name in expected
    }
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        raise ValueError(f'elevation cloud missing fields: {missing}')
    invalid = [
        name for name, datatype in expected.items()
        if actual[name].datatype != datatype or actual[name].count != 1
    ]
    if invalid:
        raise ValueError(f'elevation cloud has invalid field types: {invalid}')
    points = point_cloud2.read_points(
        message, field_names=list(expected), skip_nans=False
    )
    rows = np.empty((len(points), 5), dtype=np.float64)
    for column, name in enumerate(expected):
        rows[:, column] = points[name]
    return rows


def create_feature_cloud(header: Header, rows: np.ndarray):
    """Create the documented mixed-type terrain feature PointCloud2."""
    rows = np.asarray(rows).reshape((-1, len(FEATURE_DTYPE.names)))
    structured = np.empty(len(rows), dtype=FEATURE_DTYPE)
    for index, name in enumerate(FEATURE_DTYPE.names):
        structured[name] = rows[:, index]
    return point_cloud2.create_cloud(
        header, FEATURE_FIELDS, structured, point_step=44
    )


def feature_cloud_numpy(message) -> np.ndarray:
    """Validate and unpack the terrain feature PointCloud2 schema."""
    expected = {
        field.name: field.datatype for field in FEATURE_FIELDS
    }
    actual = {
        field.name: field
        for field in message.fields
        if field.name in expected
    }
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        raise ValueError(f'feature cloud missing fields: {missing}')
    invalid = [
        name for name, datatype in expected.items()
        if actual[name].datatype != datatype or actual[name].count != 1
    ]
    if invalid:
        raise ValueError(f'feature cloud has invalid field types: {invalid}')
    points = point_cloud2.read_points(
        message, field_names=list(expected), skip_nans=False
    )
    rows = np.empty((len(points), len(expected)), dtype=np.float64)
    for column, name in enumerate(expected):
        rows[:, column] = points[name]
    return rows


def create_traversability_cloud(header: Header, rows: np.ndarray):
    """Create the mixed-type terrain traversability PointCloud2."""
    rows = np.asarray(rows).reshape(
        (-1, len(TRAVERSABILITY_DTYPE.names))
    )
    structured = np.empty(len(rows), dtype=TRAVERSABILITY_DTYPE)
    for index, name in enumerate(TRAVERSABILITY_DTYPE.names):
        structured[name] = rows[:, index]
    return point_cloud2.create_cloud(
        header,
        TRAVERSABILITY_FIELDS,
        structured,
        point_step=TRAVERSABILITY_DTYPE.itemsize,
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
