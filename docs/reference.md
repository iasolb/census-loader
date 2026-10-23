# census-loader reference

## Exploring the catalog

Three discovery functions browse, search, and inspect the catalog from a REPL or
notebook:

- `available()`: browse categories; `available("INCOME")` drills into a
  category or subcategory.
- `search("poverty")`: search by keyword.
- `info("MEDIAN_HH_INCOME")`: full details (name, category, dataset,
  underlying variable codes).
- `geos()`: browse geography templates.

## Output format

`pull_census` returns a `dict[str, pd.DataFrame]` keyed by friendly name and
saves it as a pickle at the configured output path. Each DataFrame has
geography columns on the left (FIPS codes and human-readable names) and data
columns on the right. Column naming depends on the series type (single variable,
multi-variable, group table); labels are fetched from the Census metadata API.
`pickle_loader` loads a saved pickle and flattens it to one DataFrame.

| Series type | Example key | Column names |
|---|---|---|
| Single variable | `TOTAL_POP` | `Total_Population` |
| Multi-variable | `HOMEOWNERSHIP_RATE` | `Homeownership_Rate__Owner occupied`, `Homeownership_Rate__Total` |
| Group table | `HH_INCOME_BRACKETS` | `Household_Income_Distribution__Less than $10,000`, `Household_Income_Distribution__$10,000 to $14,999`, ... |

## API limits

The Census API imposes request and daily usage limits. The `batch_size`
configuration value is accepted for compatibility but is not currently
enforced. The loader waits 0.5 seconds between series requests. Metadata labels
are cached for the current process session.

## Project layout

```
Census_Loader/
  pyproject.toml
  requirements.txt
  README.md
  .env-example
  src/census_loader/
    __init__.py       # public API re-exports
    utils.py          # Config, loader, discovery tools
    load.py           # pull_census entry point
    series.py         # series catalog, GEO templates, FIPS codes
```

## Config Reference

```python
Config(
    filename,       # Output filename (auto-corrects to .pkl)
    output_path,    # Directory for output files
    year=2022,      # ACS/PEP vintage year
    geo=...,        # Geography level (see below)
    state=...,      # State name or FIPS code
    county=...,     # County FIPS (3-digit)
    tract=...,      # Tract code
    series=...,     # What to pull (see below)
    batch_size=50,  # Max series per API batch
)
```

### Series selection

The `series` parameter accepts any granularity: individual series,
subcategories, categories, or a mix:

```python
series=None                                         # everything (169 series)
series="TOTAL_POP"                                  # one series
series="INCOME"                                     # whole category (18 series)
series="HOUSEHOLD_INCOME"                           # subcategory (9 series)
series=["TOTAL_POP", "INCOME", "MEDIAN_RENT"]       # mix & match
series=["POVERTY", "HOUSEHOLD_INCOME", "TOTAL_POP"] # category + subcategory + series
```

Case-insensitive. Overlapping selections deduplicate automatically.

### Geography

Pass a template name and fill in the required parameters:

```python
# All states (default)
Config(..., geo="state_all")

# All counties in one state
Config(..., geo="county_in_state", state="Massachusetts")

# Tracts in one county
Config(..., geo="tract_in_county", state="Massachusetts", county="017")

# School districts in a state
Config(..., geo="school_district_in_state", state="Massachusetts")

# All ZCTAs
Config(..., geo="zcta_all")
```

State names resolve automatically, so `"Massachusetts"` and `"25"` both work.
For edge cases not covered by templates, pass a raw dict:
`Config(..., geo={"for": "county:017", "in": "state:25"})`.

### Flattening into a single DataFrame

Merge on the shared geography columns because every series in a pull shares
the same geography:

```python
from functools import reduce
import pandas as pd

frames = list(data.values())
shared = set(frames[0].columns)
for df in frames[1:]:
    shared &= set(df.columns)

merge_keys = [c for c in shared
              if all(not pd.api.types.is_numeric_dtype(df[c]) for df in frames)]

flat = reduce(
    lambda left, right: pd.merge(left, right, on=merge_keys, how="outer"),
    frames,
)
```

### Examples

```python
# County-level dashboard data for one state
cfg = Config(
    "ma_dashboard.pkl", "./output",
    year=2022, geo="county_in_state", state="Massachusetts",
    series=["TOTAL_POP", "MEDIAN_HH_INCOME", "MEDIAN_RENT", "MEDIAN_HOME_VALUE",
            "HOMEOWNERSHIP_RATE", "HH_INCOME_BRACKETS"],
)
pull_census(cfg)

# Tract-level deep dive
cfg = Config(
    "middlesex_tracts.pkl", "./output",
    year=2022, geo="tract_in_county", state="Massachusetts", county="017",
    series=["TOTAL_POP", "MEDIAN_HH_INCOME", "POP_65_PLUS"],
)
pull_census(cfg)

# Full category pull, all states
cfg = Config("national_income.pkl", "./output", year=2022, series="INCOME")
pull_census(cfg)

# School district comparison
cfg = Config(
    "ma_schools.pkl", "./output",
    year=2022, geo="school_district_in_state", state="Massachusetts",
    series=["TOTAL_POP", "MEDIAN_HH_INCOME", "HH_INCOME_BRACKETS"],
)
pull_census(cfg)
```

### Available Categories

| Category | Series | Subcategories |
|---|---|---|
| POPULATION | 13 | TOTAL_POPULATION, AGE_DETAIL |
| RACE_ETHNICITY | 13 | RACE, HISPANIC_ORIGIN |
| NATIVITY_MIGRATION | 11 | NATIVITY, MIGRATION |
| LANGUAGE | 6 | none |
| EDUCATION | 10 | SCHOOL_ENROLLMENT, EDUCATIONAL_ATTAINMENT |
| HOUSEHOLDS | 12 | HOUSEHOLD_TYPE, MARITAL_STATUS, FERTILITY |
| INCOME | 18 | HOUSEHOLD_INCOME, EARNINGS, PUBLIC_ASSISTANCE |
| POVERTY | 12 | ACS_POVERTY, SAIPE_POVERTY |
| HEALTH_INSURANCE | 6 | ACS_HEALTH_INSURANCE, SAHIE_HEALTH_INSURANCE |
| EMPLOYMENT | 15 | EMPLOYMENT_STATUS, OCCUPATION_INDUSTRY, COMMUTING |
| HOUSING | 25 | HOUSING_UNITS, TENURE, HOME_VALUE, HOUSING_INFRASTRUCTURE |
| DISABILITY | 5 | none |
| VETERANS | 4 | none |
| PEP_POPULATION | 6 | none |
| DECENNIAL | 9 | DECENNIAL_REDISTRICTING, DECENNIAL_DHC |
| DATA_PROFILES | 4 | none |
| **Total** | **169** | |
