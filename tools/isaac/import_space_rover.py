#!/usr/bin/env python3
"""Import the SPACE rover URDF into an Isaac Sim USD stage."""

import argparse
import os
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--urdf", required=True, help="Generated URDF path.")
    parser.add_argument("--usd", required=True, help="Output USD stage path.")
    parser.add_argument("--gui", action="store_true", help="Open Isaac Sim UI while importing.")
    parser.add_argument(
        "--enable-ros2-bridge",
        action="store_true",
        help="Enable the Isaac ROS 2 bridge extension in the generated stage session.",
    )
    return parser.parse_args()


args = parse_args()

from isaacsim import SimulationApp  # noqa: E402

simulation_app = SimulationApp({"renderer": "RaytracedLighting", "headless": not args.gui})

import omni.kit.commands  # noqa: E402
import omni.usd  # noqa: E402
from isaacsim.core.utils.extensions import enable_extension  # noqa: E402
from pxr import Gf, PhysxSchema, Sdf, UsdGeom, UsdLux, UsdPhysics, UsdShade  # noqa: E402


def add_physics_scene(stage):
    scene = UsdPhysics.Scene.Define(stage, Sdf.Path("/World/physicsScene"))
    scene.CreateGravityDirectionAttr().Set(Gf.Vec3f(0.0, 0.0, -1.0))
    scene.CreateGravityMagnitudeAttr().Set(9.80665)

    PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/World/physicsScene"))
    physx_scene = PhysxSchema.PhysxSceneAPI.Get(stage, "/World/physicsScene")
    physx_scene.CreateEnableCCDAttr(True)
    physx_scene.CreateEnableStabilizationAttr(True)
    physx_scene.CreateSolverTypeAttr("TGS")


def add_physics_material(stage, path, static_friction, dynamic_friction):
    material = UsdShade.Material.Define(stage, path)
    physics_material = UsdPhysics.MaterialAPI.Apply(material.GetPrim())
    physics_material.CreateStaticFrictionAttr().Set(static_friction)
    physics_material.CreateDynamicFrictionAttr().Set(dynamic_friction)
    physics_material.CreateRestitutionAttr().Set(0.0)
    return material


def add_lane(stage, path, pose, size, color, material):
    cube = UsdGeom.Cube.Define(stage, path)
    cube.CreateSizeAttr(1.0)
    cube.AddTranslateOp().Set(Gf.Vec3d(*pose))
    cube.AddScaleOp().Set(Gf.Vec3f(*size))
    cube.CreateDisplayColorAttr().Set([Gf.Vec3f(*color)])
    UsdPhysics.CollisionAPI.Apply(cube.GetPrim())
    UsdShade.MaterialBindingAPI.Apply(cube.GetPrim()).Bind(material)


def add_friction_course(stage):
    normal = add_physics_material(stage, "/World/Materials/normal_friction", 1.0, 1.0)
    low = add_physics_material(stage, "/World/Materials/low_friction", 0.12, 0.08)

    add_lane(
        stage,
        "/World/normal_friction_lane",
        (0.0, 0.8, -0.02),
        (5.0, 0.9, 0.04),
        (0.38, 0.39, 0.40),
        normal,
    )
    add_lane(
        stage,
        "/World/low_friction_lane",
        (0.0, -0.8, -0.02),
        (5.0, 0.9, 0.04),
        (0.88, 0.86, 0.78),
        low,
    )
    add_lane(
        stage,
        "/World/center_divider",
        (0.0, 0.0, 0.05),
        (5.0, 0.05, 0.10),
        (0.15, 0.16, 0.17),
        normal,
    )


def add_lighting(stage):
    distant_light = UsdLux.DistantLight.Define(stage, Sdf.Path("/World/DistantLight"))
    distant_light.CreateIntensityAttr(700)
    distant_light.CreateAngleAttr(0.3)


def import_urdf(stage, urdf_path):
    status, import_config = omni.kit.commands.execute("URDFCreateImportConfig")
    if not status:
        raise RuntimeError("URDFCreateImportConfig failed")

    import_config.merge_fixed_joints = False
    import_config.convex_decomp = False
    import_config.import_inertia_tensor = True
    import_config.fix_base = False
    import_config.collision_from_visuals = False
    import_config.distance_scale = 1.0

    status, prim_path = omni.kit.commands.execute(
        "URDFParseAndImportFile",
        urdf_path=str(urdf_path),
        import_config=import_config,
        get_articulation_root=True,
    )
    if not status:
        raise RuntimeError(f"URDFParseAndImportFile failed for {urdf_path}")

    prim = stage.GetPrimAtPath(prim_path)
    if prim.IsValid():
        xform = UsdGeom.Xformable(prim)
        translate_op = None
        for op in xform.GetOrderedXformOps():
            if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
                translate_op = op
                break
        if translate_op is None:
            translate_op = xform.AddTranslateOp()
        translate_op.Set(Gf.Vec3d(-2.0, 0.8, 0.18))
    return prim_path


def main():
    urdf_path = Path(args.urdf).resolve()
    usd_path = Path(args.usd).resolve()
    if not urdf_path.exists():
        raise FileNotFoundError(urdf_path)

    usd_path.parent.mkdir(parents=True, exist_ok=True)

    if args.enable_ros2_bridge:
        enable_extension("isaacsim.ros2.bridge")
    enable_extension("isaacsim.asset.importer.urdf")
    simulation_app.update()

    context = omni.usd.get_context()
    context.new_stage()
    stage = context.get_stage()
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)

    add_physics_scene(stage)
    add_friction_course(stage)
    add_lighting(stage)
    prim_path = import_urdf(stage, urdf_path)

    if not context.save_as_stage(str(usd_path)):
        raise RuntimeError(f"Could not save USD stage: {usd_path}")

    print(f"Imported rover at {prim_path}")
    print(f"Saved Isaac stage: {usd_path}")


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
