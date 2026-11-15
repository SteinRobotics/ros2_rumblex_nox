# Nox CAD design notes

All CAD commands below must be run inside the verified resource wrapper described
in [AGENTS.md](AGENTS.md). Run test modules separately; do not run a full geometry
suite concurrently with another heavy workload.

## Dimensions and joints

All lengths are in millimetres and angles in degrees. Servo dimensions and
mounting-hole positions and shared cutout profiles are defined in `common/servo_simplified.py`. Foot and body
cutout hole patterns use those same dimensions; drawing polygons retain their
original coordinates with `align=None`.

The servo rotation joint is at the front horn's outer mounting face. Bracket
joints are at the matching inner leg face, centred on the shaft hole. The
37 mm bracket opening matches the distance between the servo's outer horn
faces. Assemblies connect these joints directly, without translations or
rotations after connection. Inclined brackets also expose a `plate_mount`
joint at the centre of their outer top face.

The femur is rolled 180 degrees about its longitudinal (local Z) axis through
the midpoint between the horn faces. Its rear horn mates with the coxa; the
outgoing tibia interface follows the rolled bracket.
The tibia is likewise rolled 180 degrees about its lengthwise axis (local X),
through the horn midpoint at shaft height, so its rear horn mates with the femur.

`assembly_leg.attach_leg()` is shared by the standalone leg and complete robot.
Angles specify rotation about the mating axis; negative angles are supported.
The display pose uses 90 degrees at the femur and -90 degrees at the tibia to
place the feet below the body. These are pose settings, not dimensional fit
corrections; the old corrected zero-angle pose is not preserved.

## Remaining vendor fits

Nox retains the bottom bracket's 5.65 mm insertion and the head side bracket's
empirical registration offset. The separate `assembly_tibia_HX35H.py`
vendor-servo examples also retain their original offsets.


## Nox mesh description

`urdf/nox_mesh.urdf.xacro` and `urdf/mesh_leg.xacro` register the existing
Nox STL exports to the CAD horn mounting faces. The torso uses the checked-in
`meshes/nox/assembly_body_servo.stl`. Zero joint angles reproduce the complete
CAD assembly's leg angles (0/0/180 degrees) and head pitch (-60 degrees).
Positive URDF joint angles increase the corresponding CAD connection angle.
These joint frames differ from the simplified IK frames in `nox.urdf.xacro`;
the collision envelopes and inertias remain approximations.

The package test `test/test_nox_urdf.py` checks resource paths, the connected
joint tree and simulation configuration. With the CAD virtualenv, ROS, xacro
and PyYAML available, run `python -m unittest discover -s tests -p
test_nox_urdf.py -v` from this directory to compare STL bounds and all leg/head
mesh placements against CAD at zero and 12-degree joint angles.

