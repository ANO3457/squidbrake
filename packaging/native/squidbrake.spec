# PyInstaller spec for the native build: one folder with squidbrake(.exe) and everything it needs, no Python.
#   pip install . pyinstaller && pyinstaller packaging/native/squidbrake.spec
# The gateway's scripts are plain .py files the CLI imports by name and runs as hooks, so the installed package is
# copied in as files as well, and its third-party imports are collected whole.
import importlib.util
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

pkg = Path(importlib.util.find_spec("squidbrake").origin).parent
datas, binaries, hidden = [(str(pkg), "squidbrake")], [], []
for dep in ("fastapi", "starlette", "pydantic", "pydantic_core", "uvicorn", "sqlalchemy", "httpx", "httpcore", "anyio",
            "h11", "yaml", "dotenv", "mcp", "segno", "sse_starlette", "jsonschema", "certifi"):
    datas += collect_data_files(dep)
    binaries += collect_dynamic_libs(dep)
    hidden += collect_submodules(dep, filter=lambda m: not m.startswith("mcp.cli"))   # mcp's own CLI needs typer

# the scripts are analysed too (as top-level modules), so the standard library and packages they use come along
scripts = [p.stem for p in pkg.glob("*.py") if p.stem != "__init__"]
a = Analysis([str(Path(SPECPATH) / "entry.py")], pathex=[str(pkg)], datas=datas, binaries=binaries,
             hiddenimports=hidden + scripts + ["squidbrake.cli"], excludes=["tkinter"])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="squidbrake", console=True)
coll = COLLECT(exe, a.binaries, a.datas, name="squidbrake")
