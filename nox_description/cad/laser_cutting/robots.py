"""Laser-cut BOMs derived from the corresponding assembly builders.

Only sheet parts belong here: purchased brackets, electronics, turned spacers,
rubber toes and solid head blocks are not laser-cut sheet components.
"""

from dataclasses import dataclass
from importlib import import_module


@dataclass
class Component:
    name: str
    quantity: int
    thickness: float
    surface: object


def cutting_face(part, plane, thickness):
    """Extract a face only if it represents the complete constant-thickness part."""
    faces = [
        f
        for f in part.faces()
        if f.normal_at().dot(plane.z_dir) > 1 - 1e-07
        and abs((f.center() - plane.origin).dot(plane.z_dir)) < 1e-06
    ]
    if len(faces) != 1:
        raise ValueError(f"Expected one cutting face, found {len(faces)}")
    face = faces[0]
    from build123d import extrude

    reconstructed = extrude(face, amount=-thickness)
    if (part - reconstructed).volume + (reconstructed - part).volume > 0.0001:
        raise ValueError(
            "Part is not a uniform sheet extrusion; a flat pattern is missing"
        )
    return plane.to_local_coords(face)


def _nox_components(robot):
    """Build fresh nominal geometry without invoking exporters or the viewer."""
    if robot not in ("nox",):
        raise ValueError(f"Unknown robot {robot!r}; supported robot: nox")
    from build123d import Plane

    def module(name):
        return import_module(f"robot_{robot}.{name}")

    common = module("torso_common")
    legs = len(common.SERVO_POSITIONS.keys() - {"head"})
    parts = []

    def add(name, quantity=1, *, surface=None, thickness=None):
        source = module(name) if surface is None else None
        if surface is None:
            surface = source.build_surface()
        if thickness is None:
            thickness = getattr(source, "THICKNESS", common.THICKNESS)
        parts.append(Component(name, quantity, thickness, surface))

    for index in range(5):
        add(f"torso_layer_{index}")
    for name in ("foot_front", "foot_back", "foot_connection"):
        add(name, legs)
    slots = common.rectangle_slots_locations
    ends = [p for p in slots if abs(p.orientation.Z) > 1e-06]
    sides = [p for p in slots if abs(p.orientation.Z) <= 1e-06 and p.position.X > 0]
    chassis = module("chassis_side")
    torso = module("assembly_torso")
    height = 3 * common.THICKNESS + torso.SPACER_LENGTH_1_to_2 + torso.SPACER_LENGTH_TOP
    for name, quantity, side, h in (
        ("chassis_side_end", len(ends), False, height),
        ("chassis_side", len(sides), True, height),
        (
            "chassis_side_diagonal",
            len(common.diagonal_slots_locations),
            False,
            common.SPACER_LENGTH_TOP + 2 * common.THICKNESS,
        ),
    ):
        add(
            name,
            quantity,
            surface=chassis.build_surface(h, side=side),
            thickness=chassis.THICKNESS,
        )
    return parts


ROBOT_BUILDERS = {"nox": lambda: _nox_components("nox")}


def robot_components(robot):
    if robot not in ROBOT_BUILDERS:
        raise ValueError(
            f"Unknown robot {robot!r}; supported robots: {', '.join(ROBOT_BUILDERS)}"
        )
    return ROBOT_BUILDERS[robot]()
