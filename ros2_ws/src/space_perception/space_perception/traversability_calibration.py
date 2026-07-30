"""Generate deterministic traversability response sweeps as CSV and Markdown."""

import argparse
import csv
from pathlib import Path

import numpy as np

from space_description.rover_geometry import load_geometry, max_step_height
from space_perception.traversability import (
    compute_traversability,
    TraversabilityConfig,
)


# The step sweep's upper anchors are DERIVED, not typed. They used to read
# 56, 80, 112 mm -- the old step limit, a point past it, and the old 0.112 m
# wheel radius. After the CAD import made the wheel 0.070 m those three sampled
# a rover that no longer exists, so every regenerated calibration artifact kept
# certifying that the step penalty saturates at 56 mm. Deriving them means the
# published response curve always brackets the real limit.
_GEOMETRY = load_geometry()
_STEP_LIMIT = max_step_height(_GEOMETRY)
_WHEEL_RADIUS = _GEOMETRY['wheel_radius']

SWEEPS = {
    'slope_rad': np.deg2rad([0, 2.5, 5, 10, 15, 20, 25, 30, 35]),
    'roughness_m': np.asarray([0, 1, 2, 5, 10, 15, 25, 40]) / 1000.0,
    # Nine points, the last three being the step limit, the midpoint between it
    # and the wheel radius, and the wheel radius itself. The count matters:
    # test_traversability.py asserts the sweep produces exactly 44 rows.
    'step_height_m': np.asarray([
        0.0, 0.002, 0.005, 0.010, 0.020, 0.030,
        _STEP_LIMIT, (_STEP_LIMIT + _WHEEL_RADIUS) / 2.0, _WHEEL_RADIUS,
    ]),
    'coverage': np.asarray([0.2, 0.4, 0.6, 0.8, 1.0]),
    'confidence': np.asarray([0, 0.1, 0.25, 0.5, 0.75, 1.0]),
    'variance_m2': np.asarray([
        0.0, 0.0000125, 0.000025, 0.0001, 0.0002, 0.0004, 0.0008
    ]),
}


def calibration_rows(config=TraversabilityConfig()):
    """Evaluate controlled one-variable sweeps with production scoring code."""
    columns = {
        'slope_rad': 3,
        'roughness_m': 4,
        'step_height_m': 5,
        'variance_m2': 6,
        'coverage': 9,
        'confidence': 10,
    }
    base = np.asarray([
        0.05, 0.05, 0.1, 0.0, 0.0, 0.0, 0.0, 8, 28, 1.0, 1.0
    ])
    results = []
    for name, values in SWEEPS.items():
        for value in values:
            feature = base.copy()
            feature[columns[name]] = value
            output, _ = compute_traversability(feature[None, :], config)
            row = output[0]
            results.append({
                'sweep': name,
                'input_value': float(value),
                'traversability': float(row[3]),
                'slope_penalty': float(row[4]),
                'roughness_penalty': float(row[5]),
                'step_penalty': float(row[6]),
                'uncertainty_penalty': float(row[7]),
                'valid': int(row[9]),
                'limiting_factor': int(row[10]),
            })
    return results


def write_calibration(output_directory, config=TraversabilityConfig()):
    """Write deterministic CSV and concise Markdown response tables."""
    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    rows = calibration_rows(config)
    csv_path = directory / 'traversability_response.csv'
    with csv_path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    markdown_path = directory / 'traversability_response.md'
    lines = [
        '# Traversability synthetic response',
        '',
        '| Sweep | Input | Score | Active penalty | Valid |',
        '| --- | ---: | ---: | ---: | ---: |',
    ]
    for row in rows:
        penalties = [
            row['slope_penalty'],
            row['roughness_penalty'],
            row['step_penalty'],
            row['uncertainty_penalty'],
        ]
        score = row['traversability']
        score_text = 'NaN' if not np.isfinite(score) else f'{score:.6f}'
        lines.append(
            f'| {row["sweep"]} | {row["input_value"]:.7g} | '
            f'{score_text} | {max(penalties):.6f} | {row["valid"]} |'
        )
    markdown_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return csv_path, markdown_path


def main(args=None):
    """Run the calibration utility."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--output-directory',
        default='.',
        help='directory for traversability_response.csv and .md',
    )
    parsed = parser.parse_args(args)
    csv_path, markdown_path = write_calibration(parsed.output_directory)
    print(csv_path)
    print(markdown_path)


if __name__ == '__main__':
    main()
