"""Assemble a ready-to-push Hugging Face Space (Docker) for the webapp.

Mirrors the minimal thesis subtree the FastAPI backend needs — lib modules, the
three deployed model pickles, the ABT, the LGU boundaries, and the built frontend
— into ``webapp/hf_space/``, preserving the directory layout so the library's
relative paths resolve unchanged inside the container.

Run AFTER the data + frontend are current:

    cd thesis_main/webapp
    npm run export:data
    npm run build
    ../../.venv/bin/python deploy/build_hf_space.py

Then push ``webapp/hf_space/`` to your Space (see the chat steps / deploy/README).
"""

from __future__ import annotations

import shutil
from pathlib import Path

WEBAPP = Path(__file__).resolve().parents[1]  # thesis_main/webapp
THESIS = WEBAPP.parent  # thesis_main
DEPLOY = WEBAPP / "deploy"
OUT = WEBAPP / "hf_space"

# Space-root files copied from deploy/ templates.
ROOT_FILES = ["Dockerfile", "requirements.txt", "README.md", ".gitattributes"]

# (source path, destination relative to OUT) — layout preserved under thesis_main/.
FILES = [
    (THESIS / "Models/stratified/condo_model.pkl", "thesis_main/Models/stratified/condo_model.pkl"),
    (THESIS / "Models/stratified/houses_model.pkl", "thesis_main/Models/stratified/houses_model.pkl"),
    (THESIS / "Models/stratified/lot_model.pkl", "thesis_main/Models/stratified/lot_model.pkl"),
    (THESIS / "Models/stratified/deployment_manifest.json", "thesis_main/Models/stratified/deployment_manifest.json"),
    (THESIS / "Data/processed/abt_clean.csv", "thesis_main/Data/processed/abt_clean.csv"),
    (THESIS / "app/data/lgu_boundaries.geojson", "thesis_main/app/data/lgu_boundaries.geojson"),
    (WEBAPP / "api/main.py", "thesis_main/webapp/api/main.py"),
]

# Only the lib modules the backend actually imports (no streamlit-dependent ones).
LIB_MODULES = [
    "_cache.py",
    "config.py",
    "features.py",
    "location.py",
    "mcrai_lookup.py",
    "predict.py",
    "shap_explain.py",
]


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    for name in ROOT_FILES:
        src = DEPLOY / name
        if not src.exists():
            raise SystemExit(f"Missing deploy template: {src}")
        shutil.copy2(src, OUT / name)

    for src, rel in FILES:
        if not src.exists():
            raise SystemExit(f"Missing required source file: {src}")
        copy_file(src, OUT / rel)

    lib_src = THESIS / "app/lib"
    for module in LIB_MODULES:
        src = lib_src / module
        if not src.exists():
            raise SystemExit(f"Missing lib module: {src}")
        copy_file(src, OUT / "thesis_main/app/lib" / module)

    dist = WEBAPP / "dist"
    if not (dist / "index.html").exists():
        raise SystemExit("dist/index.html missing — run `npm run build` first.")
    shutil.copytree(dist, OUT / "thesis_main/webapp/dist")

    total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    files = sum(1 for p in OUT.rglob("*") if p.is_file())
    print(f"Assembled {OUT}")
    print(f"  {files} files, {total / 1e6:.1f} MB total")
    print("  Push this folder to your Hugging Face Space (Docker SDK).")


if __name__ == "__main__":
    main()
