"""What a stranger sees on PyPI, pinned so it cannot quietly regress.

Read as text, not with tomllib: the suite runs on Python 3.10, which has none.
"""

from pathlib import Path

PYPROJECT = (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text(
    encoding="utf-8"
)


def test_the_pypi_page_links_back_to_the_repo():
    assert "[project.urls]" in PYPROJECT
    assert 'Repository = "https://github.com/iasolb/census-loader"' in PYPROJECT


def test_the_license_is_an_spdx_expression():
    # The TOML-table form is deprecated and stops building after 2027-02-18,
    # and setuptools refuses a License classifier beside an SPDX expression.
    assert 'license = "MIT"' in PYPROJECT
    assert "License :: OSI Approved" not in PYPROJECT


def test_no_dependency_is_declared_that_nothing_imports():
    assert '"numpy"' not in PYPROJECT
