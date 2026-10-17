"""Printed output must never crash a stream that is not UTF-8.

A Windows script whose stdout is piped or redirected writes cp1252. The pull
loop printed check marks and arrows there and raised UnicodeEncodeError after
the data had already arrived, so a successful pull read as a crash
(2026-10-17). Each test runs its call under a strict cp1252 stdout, which is
what that script sees. The swap happens inside the test body because pytest
re-installs its own capture stream after fixture setup.

Offline: the client is faked exactly as in test_pull_loop.py.
"""

import io
from contextlib import contextmanager, redirect_stdout

import pandas as pd

import census_loader.utils as utils
from census_loader import load as load_module
from census_loader.utils import Config, available


class _Cp1252Out:
    def __init__(self):
        self.raw = io.BytesIO()
        self.stream = io.TextIOWrapper(
            self.raw, encoding="cp1252", errors="strict", newline="\n"
        )

    def text(self) -> str:
        self.stream.flush()
        return self.raw.getvalue().decode("cp1252")


@contextmanager
def cp1252_stdout():
    out = _Cp1252Out()
    with redirect_stdout(out.stream):
        yield out


class _FakeCensus:
    def __init__(self, key):
        self.acs5 = object()


def test_say_degrades_a_character_the_stream_cannot_encode():
    with cp1252_stdout() as out:
        utils._say("before ✓ after")
    assert out.text() == "before ? after\n"


def test_a_pull_with_a_failure_prints_cleanly_to_cp1252(monkeypatch, tmp_path):
    monkeypatch.delenv("CENSUS_API_KEY", raising=False)
    monkeypatch.setattr(utils, "load_dotenv", lambda: None)
    monkeypatch.setattr(utils.time, "sleep", lambda _: None)
    monkeypatch.setattr(utils, "Census", _FakeCensus)

    def fake_wrapped(client_attr, var_list, group_name, geo, year):
        if "FAIL" in var_list:
            raise RuntimeError("upstream said → no")
        return pd.DataFrame({"NAME": ["MA"], "GOOD": ["1"], "state": ["25"]})

    monkeypatch.setattr(utils, "_pull_wrapped", fake_wrapped)
    monkeypatch.setattr(utils, "_fetch_group_labels", lambda *a: {})
    monkeypatch.setattr(utils, "_fetch_var_labels", lambda *a: {})

    series = {
        "GOOD_SER": ("Good Series", "acs5", ("GOOD",)),
        "BAD_SER": ("Bad Series", "acs5", ("FAIL",)),
    }
    cfg = Config("enc.pkl", tmp_path, series=series, api_key="test-key")
    with cp1252_stdout() as out:
        result = load_module.pull_census(cfg)

    assert result is not None and "Good Series" in result
    text = out.text()
    assert "ok   Good Series" in text
    assert "FAIL Bad Series" in text
    assert "upstream said ? no" in text
    assert "Saved -> " in text


def test_available_prints_cleanly_to_cp1252():
    with cp1252_stdout() as out:
        available()
    assert "TOTAL" in out.text()
