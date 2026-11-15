# Split validation — 2026-11-15

All 13 packages compiled and installed locally with tests enabled, using ROS 2
Lyrical in the independent `colcon_nox` workspace. The shell initially inherited the original workspace overlay; subsequent
isolation checks use `scripts/environment.sh` to clear it explicitly. No hardware deployment, simulation session or CAD export was performed.

## Results

- Registered CTest checks: **51 passed, 2 failed, 53 total** across utilities,
  brain, movement, navigation, description, bringup and Gazebo packages.
- Focused source-tree Python checks: **69 passed, 1 failed, 5 skipped**, plus
  81 passing subtests. These overlap the registered tests and are not additional coverage totals.
- Communication/HMI/teleoperation checks in the dedicated `.venv`: **92 passed,
  1 failed, 1 skipped** (private wake-word model absent).
- Final focused checks under the clean `.venv` environment: **18 of 18 passed**,
  covering brain configuration/interpretation/sensor gaits/movement handling,
  the movement package, model descriptions and bringup.
- All movement, navigation, model, sensor-launch and setup-script checks passed.
- Python and shell syntax, local package dependency closure, CAD imports and
  documentation links checked successfully.
- The six meshes, anatomy configuration and servo calibration match the original
  Nox files byte-for-byte. The independent repository retains its preparation
  commit; the old repository's history was not imported.

## Existing test mismatches preserved

1. `test_choreography`: the checked-in metal dance includes a music action absent
   from its generator output. Running the corresponding test in the original
   repository reproduced the same failure.
2. `test_single_pose_target` / `FlyingKeepsKneesStraightAndWingsAttachedThroughoutRolls`:
   the test requires 90-degree knees while `flying.yaml` commands 80 and 110 degrees.
   The sequence, test, gait controller and single-pose implementation match the
   original source after package-name substitutions. This existing fixture
   inconsistency was retained rather than changing robot motion during the split.

3. `test_repository_catalog`: the expected sequence list omits eight existing
   sequences. Running the same test against the original repository reproduced
   the failure. Catalog code, tests and sequence files were not changed by the split
   except for package references and robot-specific documentation comments.

## Independent Python environment

`../../.venv` contains the runtime/test requirements declared in `requirements/`.
CAD libraries are not installed there. System-site packages remain available for
ROS compatibility; the activation helper disables user-site packages and clears
inherited sibling workspace paths. The generated Python node entry points use
this environment's interpreter.

After identifying the inherited old overlay, nine affected packages were rebuilt
with clean paths and the new interpreter. The generated workspace setup files,
CMake caches, runtime library resolution and Python imports were checked for old
workspace references. Runtime imports passed, and old package metadata and CAD
libraries were absent from the selected Python environment.

## Resource controls

Heavy checks ran sequentially with MemoryHigh=6G, MemoryMax=8G,
MemorySwapMax=1G, a 300-second timeout, two compiler workers and one test worker.
The initial combined brain/movement batch reached its timeout after the brain
completed. After confirming the scope was inactive and no compiler survived,
only the incomplete movement package was resumed; it completed successfully.

## Reproducibility prerequisite

The Garmin submodule remains pinned to
`7951ea641d1443e378af4e26878d07af219a403e`. The commit is present locally but was
not reachable from the configured GitHub remote during validation. It must be
published to that dependency remote before a fresh recursive clone can reproduce
this checkout. No repositories or dependency commits were pushed by this split.
