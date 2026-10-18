"""Part 2 data pull - tract-level ACS 2017-2021 5-year (Census summary files) + Census cartographic tract shapes for Fairfax County.

Joins the downloaded data to the county's Vulnerability Index CSV by GEOID.
Outputs: data/processed/fairfax_tracts.gpkg (layer 'tracts'), data/processed/fairfax_tracts.csv
Usage  : python -P scripts/02_fetch_tract_data.py <project_root>
"""
import io
import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import requests

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
RAW, PROC = ROOT / "data/raw", ROOT / "data/processed"
STATE, COUNTY = "51", "059"

# ---------------------------------------------------------------- ACS variables
V = {
    # Nativity & citizenship (B05002)
    "B05002_001E": "pop_nativity", "B05002_013E": "foreign_born", "B05002_013M": "foreign_born_moe",
    "B05002_014E": "naturalized", "B05002_021E": "noncitizen",
    "B05002_015E": "nat_europe", "B05002_016E": "nat_asia", "B05002_017E": "nat_africa", "B05002_019E": "nat_latam",
    "B05002_022E": "non_europe", "B05002_023E": "non_asia", "B05002_024E": "non_africa", "B05002_026E": "non_latam",
    # Race / Hispanic origin (B03002)
    "B03002_001E": "pop_race", "B03002_003E": "nh_white", "B03002_004E": "nh_black", "B03002_006E": "nh_asian",
    "B03002_009E": "nh_multi", "B03002_012E": "hispanic",
    # Sex by age (B01001) and median age (B01002)
    "B01001_001E": "pop_total", "B01001_002E": "male", "B01002_001E": "median_age",
}
for i in range(3, 7):
    V[f"B01001_{i:03d}E"] = f"m_u18_{i}"
    V[f"B01001_{i + 24:03d}E"] = f"f_u18_{i}"
for i in range(20, 26):
    V[f"B01001_{i:03d}E"] = f"m_65_{i}"
    V[f"B01001_{i + 24:03d}E"] = f"f_65_{i}"


def fetch_acs():
    """Stream the ACS 2021 5-yr table-based summary files (no API key needed) and keep Fairfax tracts only."""
    base = "https://www2.census.gov/programs-surveys/acs/summary_file/2021/table-based-SF/data/5YRData/"
    prefix = f"1400000US{STATE}{COUNTY}"
    frames = []
    for table in sorted({k.split("_")[0] for k in V}):
        cache = RAW / f"acs2021_{table.lower()}_fairfax_tracts.csv"
        if not cache.exists():
            keep = []
            with requests.get(f"{base}acsdt5y2021-{table.lower()}.dat", stream=True, timeout=300) as r:
                r.raise_for_status()
                for i, line in enumerate(r.iter_lines(chunk_size=1 << 20)):
                    if i == 0 or line.startswith(prefix.encode()):
                        keep.append(line.decode("utf-8"))
            cache.write_text("\n".join(keep), encoding="utf-8")
        df = pd.read_csv(cache, sep="|", dtype={"GEO_ID": str})
        df["GEOID"] = df.GEO_ID.str[-11:]
        df = df.set_index("GEOID")
        # API-style name B05002_013E -> summary-file column B05002_E013
        cols = {k: f"{k.split('_')[0]}_{k[-1]}{k.split('_')[1][:-1]}" for k in V if k.startswith(table)}
        frames.append(df[list(cols.values())].rename(columns={v: k for k, v in cols.items()}))
    acs = pd.concat(frames, axis=1).apply(pd.to_numeric, errors="coerce")
    acs = acs.where(acs > -1e8)  # Census uses -666666666 etc. for "not available"
    return acs.rename(columns=V)


def fetch_tracts():
    url = "https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_51_tract_500k.zip"
    dest = RAW / "cb_2021_51_tract_500k.zip"
    if not dest.exists():
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        dest.write_bytes(r.content)
    g = gpd.read_file(f"zip://{dest.as_posix()}")
    return g[g.COUNTYFP == COUNTY][["GEOID", "NAMELSAD", "ALAND", "geometry"]]


acs = fetch_acs()
a = pd.DataFrame(index=acs.index)
a["pop_total"] = acs.pop_total
pct = lambda n, d: 100 * n / d.replace(0, np.nan)
a["pct_foreign_born"] = pct(acs.foreign_born, acs.pop_nativity)
a["foreign_born_moe"] = acs.foreign_born_moe
a["pct_noncitizen"] = pct(acs.noncitizen, acs.pop_nativity)
a["pct_fb_naturalized"] = pct(acs.naturalized, acs.foreign_born)
a["pct_born_asia"] = pct(acs.nat_asia + acs.non_asia, acs.pop_nativity)
a["pct_born_latam"] = pct(acs.nat_latam + acs.non_latam, acs.pop_nativity)
a["pct_born_africa"] = pct(acs.nat_africa + acs.non_africa, acs.pop_nativity)
a["pct_born_europe"] = pct(acs.nat_europe + acs.non_europe, acs.pop_nativity)
a["pct_hispanic"] = pct(acs.hispanic, acs.pop_race)
a["pct_nh_white"] = pct(acs.nh_white, acs.pop_race)
a["pct_nh_black"] = pct(acs.nh_black, acs.pop_race)
a["pct_nh_asian"] = pct(acs.nh_asian, acs.pop_race)
a["pct_nh_multiracial"] = pct(acs.nh_multi, acs.pop_race)
a["median_age"] = acs.median_age
a["pct_under18"] = pct(acs.filter(like="_u18_").sum(axis=1), acs.pop_total)
a["pct_65plus"] = pct(acs.filter(like="_65_").sum(axis=1), acs.pop_total)
a["pct_male"] = pct(acs.male, acs.pop_total)
a["foreign_born"] = acs.foreign_born
a["noncitizen"] = acs.noncitizen
a = a.reset_index()

vi = pd.read_csv(RAW / "vulnerability_index_2021.csv", dtype={"GEOID": str}, encoding="utf-8-sig")
vi.columns = vi.columns.str.strip()
vi = vi.rename(columns={"Vulnerability Index": "vuln_index", "Vulnerability Index Description": "vuln_category",
                        "Median Household Income": "median_hh_income",
                        "Percent Speak English Less than Well": "vi_pct_limited_english"})
vi = vi[["GEOID", "vuln_index", "vuln_category", "median_hh_income", "vi_pct_limited_english"]]

tracts = fetch_tracts()
print(f"tracts in shapefile: {len(tracts)} | ACS tracts: {len(a)} | vulnerability index rows: {len(vi)}")
print("  ACS GEOIDs missing from shapes:", sorted(set(a.GEOID) - set(tracts.GEOID)))
print("  Vulnerability GEOIDs missing from shapes:", sorted(set(vi.GEOID) - set(tracts.GEOID)))
print("  Shapes missing a vulnerability score:", sorted(set(tracts.GEOID) - set(vi.GEOID)))

gdf = tracts.merge(a, on="GEOID", how="left").merge(vi, on="GEOID", how="left")
gdf["low_pop_flag"] = gdf.pop_total < 500
gdf = gdf.to_crs(2283)  # NAD83 / Virginia North (US ft) - good for area/distance

# ---------------------------------------------------------------- sanity checks
tot = gdf.pop_total.sum()
fb = 100 * gdf.foreign_born.sum() / tot
print(f"County total population (sum of tracts): {tot:,.0f}")
print(f"County % foreign-born (pooled): {fb:.1f}%")
print(f"Low-population tracts (<500 people): {gdf.low_pop_flag.sum()} -> {list(gdf.loc[gdf.low_pop_flag, 'NAMELSAD'])}")
area_sqmi = gdf.dissolve().area.iloc[0] / 27_878_400
bnd = pd.read_csv(RAW / "county_boundary.csv")
# Boundary CSV area is in Web-Mercator m^2; scale by cos^2(latitude) to get true area.
true_bnd = bnd.Shape__Area.iloc[0] * np.cos(np.radians(38.83)) ** 2 / 2_589_988
print(f"Area check: dissolved tracts {area_sqmi:,.1f} sq mi (excl. Fairfax City & Falls Church holes) vs "
      f"county boundary file ~{true_bnd:,.1f} sq mi")

gdf.to_file(PROC / "fairfax_tracts.gpkg", layer="tracts", driver="GPKG")
gdf.drop(columns="geometry").to_csv(PROC / "fairfax_tracts.csv", index=False)
print("wrote", PROC / "fairfax_tracts.gpkg")
