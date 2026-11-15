# Nox Python environment

Run `bash scripts/setup_venv.sh` from the repository to populate only this
workspace's `.venv`. Use `--runtime-only` for deployment without the development
test dependencies. Activate it with `source scripts/environment.sh`.

- `runtime.txt`: Python runtime and package-build dependencies used by this robot.
- `test.txt`: runtime dependencies plus pytest and ONNX model validation.
- CAD dependencies stay in `nox_description/cad/requirements-laser.txt` and the
  separate CAD environment; they are not installed into the workspace environment.

ROS, colcon, PyAudio, and other available native/system packages are reused through
`--system-site-packages`. User-site packages and inherited sibling ROS overlays are
excluded by the environment helper. Do not install ROS or a conflicting OpenCV
wheel from pip; the camera stack, when present, uses ROS cv_bridge and apt OpenCV.

openWakeWord 0.6.0 is installed separately with `--no-deps`: this code uses its ONNX
backend, and `runtime.txt` lists the required backend dependencies. Its unused
`tflite-runtime` dependency has no compatible wheel for this system Python. A raw
`pip check` can therefore report that optional-backend metadata requirement;
no TensorFlow/TFLite package is installed merely to satisfy it.

Private wake-word models and Google credentials are not part of the repository or
virtual environment installation. Supply them according to the communication docs.
