# Nox CAD

`robot_nox.py` and `robot_nox/` contain the complete robot assembly and its
components. `boards/`, `common/` and `utils/` provide the helpers used by this model.
Use a local `.venv` with build123d and the dependencies in `requirements-laser.txt`.
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
