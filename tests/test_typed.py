import os
import sys
from pathlib import Path


def _classifier_declared(pyproject: Path, classifier: str) -> bool:
    """Is this classifier declared in pyproject.toml?

    `tomllib` IS STDLIB ONLY FROM 3.11 and this package supports >=3.10, so a
    bare `import tomllib` failed COLLECTION on the oldest Python it claims to
    support. Measured on CI 2026-09-17: 3.11 green, 3.10 red with
    `ModuleNotFoundError: No module named 'tomllib'`, and because the publish
    job is gated on the tests, the release never ran at all.

    On 3.10 this asserts against the file TEXT rather than skipping. A skipped
    test here would read as green while asserting nothing, which is precisely
    the fault this test was written to catch.
    """
    if sys.version_info >= (3, 11):
        import tomllib

        with pyproject.open("rb") as fh:
            data = tomllib.load(fh)
        return classifier in data.get("project", {}).get("classifiers", [])
    return classifier in pyproject.read_text(encoding="utf-8")


def _repo_root_from_test_file() -> Path:
    # The test file sits under <repo>/tests/test_typed.py
    # Resolve repo root by going up from this file's directory.
    return Path(__file__).resolve().parents[1]


def test_pyproject_classifiers_include_typing_and_license():
    root = _repo_root_from_test_file()
    pyproject = root / "pyproject.toml"
    assert pyproject.exists(), f"pyproject.toml not found at {pyproject}"

    assert _classifier_declared(pyproject, "Typing :: Typed"), \
        "Typing :: Typed classifier missing in pyproject.toml [project].classifiers"
    assert _classifier_declared(pyproject, "License :: OSI Approved :: MIT License"), \
        "MIT license classifier missing from pyproject.toml [project].classifiers"

    # Ensure the package ships py.typed marker in the installed source tree layout
    pytyped_marker = root / "src" / "census_loader" / "py.typed"
    assert pytyped_marker.exists(), f"py.typed marker missing at {pytyped_marker}"
