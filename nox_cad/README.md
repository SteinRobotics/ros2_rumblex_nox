# Nox CAD

`robot_nox.py` and `robot_nox/` contain the complete robot assembly and its
components. `boards/`, `common/` and `utils/` provide the helpers used by this model.
Create a local CAD environment with Python 3.11–3.14:

```bash
python3 -m venv .venv
.venv/bin/python -I -m pip install --upgrade pip
.venv/bin/python -I -m pip install -r requirements-cad.txt
source .venv/bin/activate
```

This includes build123d, OCP CAD Viewer, IPython kernel support, and the laser-cutting
dependencies in `requirements-laser.txt`. In VS Code, select `.venv/bin/python`
as the Python interpreter and use OCP CAD Viewer extension version 4.2.x to match
the Python viewer package.
The `-I` flag keeps pip isolated from packages exposed by a sourced ROS environment.

Imported vendor assets and generated exports are local, ignored files; obtain any
required vendor geometry separately. Tracked runtime meshes remain in `../meshes/nox/`.

Read [AGENTS.md](AGENTS.md) before running CAD jobs. Run one bounded job at a time,
with the memory limits and timeout documented there. Do not regenerate all meshes
as a routine software check.

From this directory, run `.venv/bin/python robot_nox.py` inside the resource wrapper
for assembly export. `generate_dxf.py --output <new-directory>` generates thickness-separated
laser-cut jobs for Nox; use `--help` for sheet size, kerf and nesting options.
Outputs use only the `nox` directory. Retained tests validate this model and shared helpers.

See [design notes](DESIGN.md) for mounting conventions, mechanical relationships and model validation.
