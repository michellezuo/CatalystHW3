#!/usr/bin/env bash
# Re-run the whole analysis from scratch: python packages needed are listed in README.md
set -e
R="$(cd "$(dirname "$0")" && pwd)"
python -P "$R/scripts/01_county_descriptive.py" "$R"
python -P "$R/scripts/02_fetch_tract_data.py" "$R"
python -P "$R/scripts/03_tract_stats.py" "$R"
python -P "$R/scripts/04_spatial.py" "$R"
python -P "$R/scripts/05_export_tables.py" "$R"
