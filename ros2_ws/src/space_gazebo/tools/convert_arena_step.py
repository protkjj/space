#!/usr/bin/env python3
"""Deterministically tessellate the arena STEP source with FreeCAD."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


EXPECTED_SPANS_MM = (3200.0, 550.0, 4000.0)
SPAN_TOLERANCE_MM = 0.1


def _arguments() -> argparse.Namespace:
    package = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--source',
        type=Path,
        default=package / 'assets/source_cad/arena_test_slope_v04.stp',
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=package / 'models/arena_test_slope_v04/meshes',
    )
    parser.add_argument('--visual-linear-deflection-mm', type=float, default=0.5)
    parser.add_argument('--visual-angular-deflection-deg', type=float, default=5.0)
    parser.add_argument('--visual-refinement-passes', type=int, default=1)
    parser.add_argument('--collision-linear-deflection-mm', type=float, default=10.0)
    parser.add_argument(
        '--collision-angular-deflection-deg', type=float, default=25.0
    )
    arguments = sys.argv[1:]
    if arguments and Path(arguments[0]).resolve() == Path(__file__).resolve():
        # FreeCADCmd executes scripts as modules and retains the script path in
        # sys.argv, unlike the regular Python interpreter.
        arguments = arguments[1:]
    return parser.parse_args(arguments)


def _bounds(shape: object) -> str:
    box = shape.BoundBox
    return (
        f'X=[{box.XMin:.6f}, {box.XMax:.6f}] mm, '
        f'Y=[{box.YMin:.6f}, {box.YMax:.6f}] mm, '
        f'Z=[{box.ZMin:.6f}, {box.ZMax:.6f}] mm'
    )


def _span_tuple(shape: object) -> tuple[float, float, float]:
    box = shape.BoundBox
    return box.XLength, box.YLength, box.ZLength


def _validate_expected_spans(shape: object) -> None:
    spans = _span_tuple(shape)
    for axis, actual, expected in zip('XYZ', spans, EXPECTED_SPANS_MM):
        if abs(actual - expected) > SPAN_TOLERANCE_MM:
            raise ValueError(
                f'{axis} span {actual:.6f} mm differs from expected '
                f'{expected:.6f} mm by more than {SPAN_TOLERANCE_MM} mm'
            )


def _write_stl(
    mesh_part: object,
    shape: object,
    path: Path,
    linear: float,
    angular_degrees: float,
    refinement_passes: int = 0,
) -> object:
    mesh = mesh_part.meshFromShape(
        Shape=shape,
        LinearDeflection=linear,
        AngularDeflection=angular_degrees * 3.141592653589793 / 180.0,
        Relative=False,
    )
    if mesh.CountFacets <= 0 or mesh.CountPoints <= 0:
        raise ValueError(f'tessellation produced an empty mesh for {path.name}')
    for _ in range(refinement_passes):
        mesh.refine()
    # STL has no unit metadata. Native millimetres are retained and every
    # runtime consumer applies the same explicit 0.001 scale.
    mesh.write(str(path))
    return mesh


def main() -> int:
    args = _arguments()
    if not args.source.is_file():
        print(f'error: STEP source does not exist: {args.source}', file=sys.stderr)
        return 2
    try:
        import FreeCAD  # type: ignore[import-not-found]
        import Import  # type: ignore[import-not-found]
        import MeshPart  # type: ignore[import-not-found]
        import Part  # type: ignore[import-not-found]
    except ImportError:
        print(
            'error: FreeCAD modules FreeCAD, Import, Part, and MeshPart are '
            'required. Run this script with FreeCADCmd/freecadcmd.',
            file=sys.stderr,
        )
        return 3

    document = FreeCAD.newDocument('arena_step_conversion')
    Import.insert(str(args.source.resolve()), document.Name)
    document.recompute()
    imported = list(document.Objects)
    shaped = [
        obj for obj in imported
        if hasattr(obj, 'Shape') and not obj.Shape.isNull()
    ]
    valid = [obj for obj in shaped if obj.Shape.isValid()]
    if not valid:
        print(
            f'error: STEP import produced no valid shapes: {args.source}',
            file=sys.stderr,
        )
        return 4
    shape = Part.makeCompound([obj.Shape for obj in valid])
    if shape.isNull() or not shape.isValid():
        print('error: imported shape compound is empty or invalid', file=sys.stderr)
        return 5

    print(f'Source: {args.source}')
    print(f'FreeCAD: {".".join(FreeCAD.Version()[:3])}')
    print(f'Imported objects: {len(imported)}')
    print(f'Objects with shapes: {len(shaped)}; valid shapes: {len(valid)}')
    print(f'Solids: {len(shape.Solids)}; shells: {len(shape.Shells)}')
    print(f'Source bounding box: {_bounds(shape)}')
    print(f'Watertight solids: {all(s.isClosed() for s in shape.Solids)}')
    print('Units: millimetres (STEP SI_UNIT .MILLI.,.METRE.)')
    try:
        _validate_expected_spans(shape)
    except ValueError as error:
        print(f'error: {error}', file=sys.stderr)
        return 6
    print('Expected 3200 x 550 x 4000 mm source spans: validated')
    print(
        'Runtime orientation: native mesh retained; consumers rotate +90 deg '
        'about X and apply scale 0.001'
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = (
        (
            'visual',
            args.visual_linear_deflection_mm,
            args.visual_angular_deflection_deg,
            args.visual_refinement_passes,
            'arena_visual.stl',
        ),
        (
            'collision',
            args.collision_linear_deflection_mm,
            args.collision_angular_deflection_deg,
            0,
            'arena_collision.stl',
        ),
    )
    meshes = {}
    for label, linear, angular, refinements, filename in outputs:
        path = args.output_dir / filename
        mesh = _write_stl(
            MeshPart, shape, path, linear, angular, refinements
        )
        meshes[label] = mesh
        print(
            f'{label}: {path} | bounds {_bounds(mesh)} | '
            f'{mesh.CountPoints} vertices | {mesh.CountFacets} triangles | '
            f'linear={linear} mm angular={angular} deg '
            f'refinements={refinements} | scale 0.001',
            flush=True,
        )
    if meshes['collision'].CountFacets >= meshes['visual'].CountFacets:
        print(
            'error: collision mesh is not coarser than visual mesh '
            f'({meshes["collision"].CountFacets} >= '
            f'{meshes["visual"].CountFacets})',
            file=sys.stderr,
        )
        return 7
    FreeCAD.closeDocument(document.Name)
    return 0


if (
    __name__ == '__main__'
    or Path(sys.executable).name.lower() == 'freecadcmd'
):
    raise SystemExit(main())
