import os
from pathlib import Path
import tomllib


def _repo_root_from_test_file() -> Path:
    # The test file sits under <repo>/tests/test_typed.py
    # Resolve repo root by going up from this file's directory.
    return Path(__file__).resolve().parents[1]


def test_pyproject_classifiers_include_typing_and_license():
    root = _repo_root_from_test_file()
    pyproject = root / "pyproject.toml"
    assert pyproject.exists(), f"pyproject.toml not found at {pyproject}"

    with pyproject.open("rb") as f:
        data = tomllib.load(f)

    classifiers = data.get("project", {}).get("classifiers", [])
    assert "Typing :: Typed" in classifiers, "Typing :: Typed classifier missing in pyproject.toml [project].classifiers"
    assert "License :: OSI Approved :: MIT License" in classifiers, "MIT license classifier missing from pyproject.toml [project].classifiers"

    # Ensure the package ships py.typed marker in the installed source tree layout
    pytyped_marker = root / "src" / "census_loader" / "py.typed"
    assert pytyped_marker.exists(), f"py.typed marker missing at {pytyped_marker}"
