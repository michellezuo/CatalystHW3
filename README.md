# Fairfax County — Immigration & Demographics analysis

**Start here:** `outputs/slide_guide.md` (slide-by-slide content), then `figures/` (18 PNGs, 300 dpi), and `outputs/results_tables.xlsx` (all numbers).

| Script | What it does |
|---|---|
| `scripts/01_county_descriptive.py` | Non-spatial county analysis of your two multiracial CSVs + margin-of-error z-tests (figs 01–06) |
| `scripts/02_fetch_tract_data.py` | Downloads ACS 2017–21 tract data (Census summary files) + tract shapes; joins the Vulnerability Index |
| `scripts/03_tract_stats.py` | Tract summary stats, correlations, OLS regression (figs 07–10) |
| `scripts/04_spatial.py` | Choropleths, global Moran's I, LISA, bivariate LISA (figs 11–18) |
| `scripts/05_export_tables.py` | Combines result CSVs into `outputs/results_tables.xlsx` |

## Data sources

**Provided CSVs** (copies are in `data/raw/`)

| File | Dataset | Link |
|---|---|---|
| `B05002_multiracial_2021.csv` | U.S. Census Bureau, ACS 2017–2021 5-Year Selected Population Tables, **B05002** *Place of Birth by Nativity and Citizenship Status*, Two or More Races iterations, Fairfax County, VA | [data.census.gov – ACSDT5YSPT2021.B05002](https://data.census.gov/table/ACSDT5YSPT2021.B05002?g=050XX00US51059) |
| `S0201_multiracial_2024.csv` | U.S. Census Bureau, ACS 2024 1-Year **S0201** *Selected Population Profile*, Two or More Races iterations, Fairfax County, VA | [data.census.gov – ACSSPP1Y2024.S0201](https://data.census.gov/table/ACSSPP1Y2024.S0201?g=050XX00US51059) |
| `vulnerability_index_2021.csv` | Fairfax County, *Vulnerability Index – Census Tract 2021* (ACS 2017–21 based; Office of the County Executive) | [Feature service](https://services1.arcgis.com/ioennV6PpG5Xodq0/ArcGIS/rest/services/Vulnerability_Index_Census_Tract_2021/FeatureServer/0) · [Fairfax County Open Geospatial Data hub](https://data-fairfaxcountygis.opendata.arcgis.com/) |
| `county_boundary.csv` | Fairfax County, *Fairfax County Boundary* (IT GIS Division) | [Feature service](https://services1.arcgis.com/ioennV6PpG5Xodq0/ArcGIS/rest/services/Fairfax_County_Boundary/FeatureServer) · [Fairfax County Open Geospatial Data hub](https://data-fairfaxcountygis.opendata.arcgis.com/) |

On data.census.gov, the race-group iterations (Two or More Races, Two races with/without Some Other Race, etc.) are chosen under **Filters → Race and Ethnicity**. The link opens the table for Fairfax County, but you may need to pick those groups again.

**Downloaded by `scripts/02_fetch_tract_data.py`**

| Dataset | Link |
|---|---|
| ACS 2017–2021 5-Year table-based summary files, tables **B05002** (nativity/citizenship/region of birth), **B03002** (Hispanic origin by race), **B01001** (sex by age), **B01002** (median age); all tracts in Fairfax County (state 51, county 059) | [Census summary file directory](https://www2.census.gov/programs-surveys/acs/summary_file/2021/table-based-SF/data/5YRData/) · e.g. [acsdt5y2021-b05002.dat](https://www2.census.gov/programs-surveys/acs/summary_file/2021/table-based-SF/data/5YRData/acsdt5y2021-b05002.dat) · [documentation](https://www.census.gov/programs-surveys/acs/data/summary-file.html) |
| Census 2021 cartographic boundary file, Virginia census tracts (1:500k) | [cb_2021_51_tract_500k.zip](https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_51_tract_500k.zip) · [about cartographic boundary files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html) |

The Census API (api.census.gov) now requires a key, so the script uses the bulk summary files instead. They contain the same ACS estimates.
