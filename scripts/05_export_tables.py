"""Combine all result CSVs into outputs/results_tables.xlsx (one sheet each).
Usage: python -P scripts/05_export_tables.py <project_root>
"""
import sys
from pathlib import Path
import pandas as pd

OUT = (Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")) / "outputs"
SHEETS = {
    "county_profile_2024": "county_S0201_2024_profile.csv",
    "county_B05002_2021": "county_B05002_2021_summary.csv",
    "county_ztests": "county_significance_tests.csv",
    "county_region_2021": "county_region_of_birth_2021.csv",
    "county_region_2024": "county_region_of_birth_2024_pct.csv",
    "tract_summary": "tract_summary_statistics.csv",
    "tract_top10_fb": "tract_top10_foreign_born.csv",
    "tract_correlations": "tract_correlations.csv",
    "tract_regression": "tract_regression_coefficients.csv",
    "morans_I": "spatial_global_morans_I.csv",
    "bivariate_morans_I": "spatial_bivariate_morans_I.csv",
    "lisa_clusters": "spatial_lisa_clusters.csv",
}
with pd.ExcelWriter(OUT / "results_tables.xlsx") as xw:
    pd.DataFrame({"sheet": list(SHEETS), "source_csv": list(SHEETS.values())}).to_excel(xw, sheet_name="contents", index=False)
    for name, f in SHEETS.items():
        pd.read_csv(OUT / f).to_excel(xw, sheet_name=name, index=False)
print("wrote", OUT / "results_tables.xlsx")
