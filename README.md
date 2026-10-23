# census-loader

Readable names for U.S. Census Bureau data, returned as pandas objects.

[![PyPI version](https://img.shields.io/pypi/v/census-loader)](https://pypi.org/project/census-loader/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/census-loader)](https://pypi.org/project/census-loader/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/iasolb/census-loader/blob/main/LICENSE)
[![Tests](https://github.com/iasolb/census-loader/actions/workflows/tests.yml/badge.svg)](https://github.com/iasolb/census-loader/actions/workflows/tests.yml)

## Features

- Maps friendly series names to Census Bureau variables and datasets.
- Selects data using geography templates or Census geography parameters.
- Returns results as pandas DataFrames and saves them as pickle files.
- Provides catalog discovery with `available`, `search`, `info`, and `geos`.

## Installation

```bash
pip install census-loader
```

The Census API requires a key. Get a free key at
https://api.census.gov/data/key_signup.html, then set `CENSUS_API_KEY` in the
environment or in a `.env` file in the project root:

```dotenv
CENSUS_API_KEY=your_key_here
```

Alternatively, pass the key as `api_key` to `Config`.

## Quick start

```python
from census_loader import Config, pull_census

cfg = Config(
    "ma_counties.pkl", "./output",
    year=2022,
    geo="county_in_state",
    state="Massachusetts",
    series=["TOTAL_POP", "MEDIAN_HH_INCOME", "MEDIAN_RENT"],
)

result = pull_census(cfg)   # dict of DataFrames keyed by friendly name
result["Median_Household_Income"]
```

## Documentation

See the [API reference](https://github.com/iasolb/census-loader/blob/main/docs/reference.md)
for configuration options, series selection, geography templates, output details,
and catalog categories.

## Contributing

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT, under the [MIT License](https://github.com/iasolb/census-loader/blob/main/LICENSE).
