"""Part 2 - geospatial analysis: choropleth maps, global Moran's I, LISA clusters, bivariate Moran's I.

Outputs: figures/11-17_*.png, outputs/spatial_*.csv
Usage  : python -P scripts/04_spatial.py <project_root>
"""
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mapclassify
from matplotlib.patches import Patch
from libpysal.weights import Queen
from esda.moran import Moran, Moran_Local, Moran_BV, Moran_Local_BV

sys.path.insert(0, str(Path(__file__).resolve().parent))
import style
import vars as V

warnings.filterwarnings("ignore")
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
FIG, OUT, PROC = ROOT / "figures", ROOT / "outputs", ROOT / "data/processed"
style.apply()
SEED, PERM = 2026, 999
SRC = "Source: ACS 2017-2021 5-year; Census cartographic tract boundaries 2021; Fairfax County Vulnerability Index 2021."

g_all = gpd.read_file(PROC / "fairfax_tracts.gpkg", layer="tracts")
county = g_all.dissolve()
g = g_all[~g_all.low_pop_flag & g_all[list(V.ALL)].notna().all(axis=1)].copy().reset_index(drop=True)
excluded = g_all[~g_all.GEOID.isin(g.GEOID)]
print(f"analysis tracts: {len(g)}; excluded (hatched on maps): {list(excluded.NAMELSAD)}")

w = Queen.from_dataframe(g, use_index=False)
w.transform = "r"
print(f"Queen weights: mean neighbors {w.mean_neighbors:.1f}, islands {w.islands}")


def base_map(ax):
    ax.set_axis_off()
    excluded.plot(ax=ax, facecolor="none", edgecolor=style.MUTED, hatch="///", linewidth=0.3)
    county.boundary.plot(ax=ax, color=style.INK2, linewidth=0.9)


def map_furniture(ax):
    """North arrow + 5-mile scale bar (CRS is in US feet)."""
    x0, y0, x1, y1 = county.total_bounds
    ax.annotate("N", xy=(x1 - 0.03 * (x1 - x0), y1 - 0.02 * (y1 - y0)),
                xytext=(x1 - 0.03 * (x1 - x0), y1 - 0.12 * (y1 - y0)),
                arrowprops=dict(arrowstyle="-|>", color=style.INK2, lw=1.2), ha="center", fontsize=10, color=style.INK2)
    mile = 5280
    sx, sy = x0 + 0.02 * (x1 - x0), y0 + 0.03 * (y1 - y0)
    ax.plot([sx, sx + 5 * mile], [sy, sy], color=style.INK2, lw=2.5, solid_capstyle="butt")
    ax.text(sx + 2.5 * mile, sy + 0.015 * (y1 - y0), "5 miles", ha="center", fontsize=8.5, color=style.INK2)


def choropleth(ax, col, title, cmap=style.SEQ_BLUE, k=5, fmt="{:.0f}"):
    base_map(ax)
    cl = mapclassify.Quantiles(g[col], k=k)
    g.assign(_c=cl.yb).plot(ax=ax, column="_c", cmap=cmap, edgecolor=style.SURFACE, linewidth=0.25,
                            categorical=False, vmin=0, vmax=k - 1)
    edges = [g[col].min()] + list(cl.bins)
    handles = [Patch(facecolor=cmap(i / (k - 1)), label=f"{fmt.format(edges[i])}–{fmt.format(edges[i + 1])}")
               for i in range(k)]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.97, 0.0), fontsize=8.5, title="Quintiles",
              title_fontsize=9, handlelength=1.2, borderaxespad=0.2)
    ax.set_title(title, fontsize=12)


def map_grid(cols, fname, suptitle, cmap=style.SEQ_BLUE, subtitle=None):
    n = len(cols)
    ncol = 2 if n <= 4 else 4
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(6.4 * ncol, 5.6 * nrow))
    for ax, c in zip(np.atleast_1d(axes).flat, cols):
        choropleth(ax, c, V.ALL[c], cmap=cmap)
    map_furniture(np.atleast_1d(axes).flat[0])
    fig.suptitle(suptitle, x=0.01, ha="left", fontsize=17, fontweight="semibold", color=style.INK)
    if subtitle:
        fig.text(0.01, 0.935 if nrow > 1 else 0.88, subtitle, fontsize=11, color=style.INK2)
    style.source_note(fig, SRC + " Hatched = excluded (fewer than 500 residents or no data); holes = Fairfax City & Falls Church.")
    fig.tight_layout(rect=(0, 0.03, 1, 0.92 if nrow > 1 else 0.86))
    style.save(fig, FIG / fname)


# ---------------------------------------------------------------- choropleths
map_grid(list(V.IMMIGRATION), "11_maps_immigration.png", "Where Fairfax's immigrants live",
         subtitle="Darker = higher share of tract residents. Asian-born residents concentrate in the west/center; Latin American-born in the east and along Route 1.")
map_grid(["pct_hispanic", "pct_nh_asian", "pct_nh_black", "pct_nh_white"], "12_maps_race_ethnicity.png",
         "Race & ethnicity across Fairfax County tracts", subtitle="Share of tract residents in each group (quintiles).")
map_grid(["median_age", "pct_under18", "pct_65plus", "pct_male"], "13_maps_age_sex.png",
         "Age & sex across Fairfax County tracts", cmap=style.SEQ_ORANGE,
         subtitle="Orange ramp = age/sex measures. Sex ratio is nearly uniform; age shows clear pockets.")

fig, ax = plt.subplots(figsize=(8.5, 7.2))
choropleth(ax, "vuln_index", "Vulnerability Index (1 = very low, 5 = very high)", cmap=style.SEQ_ORANGE, fmt="{:.1f}")
map_furniture(ax)
fig.suptitle("Context: Fairfax County Vulnerability Index", x=0.01, ha="left", fontsize=15, fontweight="semibold")
style.source_note(fig, "Source: Fairfax County Vulnerability Index (tract, 2017-2021).")
style.save(fig, FIG / "14_map_vulnerability_index.png")

# ---------------------------------------------------------------- global Moran's I
rows = []
morans = {}
for c, lab in V.ALL.items():
    np.random.seed(SEED)
    mi = Moran(g[c].values, w, permutations=PERM)
    morans[c] = mi
    rows.append(dict(variable=lab, morans_I=mi.I, expected_I=mi.EI, z_score=mi.z_sim, pseudo_p=mi.p_sim,
                     interpretation="Strong clustering" if mi.I >= 0.5 else
                     "Moderate clustering" if mi.I >= 0.3 else
                     "Weak clustering" if mi.I > 0 and mi.p_sim < 0.05 else "No significant pattern"))
res = pd.read_csv(PROC / "ols_residuals.csv", dtype={"GEOID": str})
gr = g.merge(res, on="GEOID")
for col, lab in [("resid_m1", "OLS residuals, model 1"), ("resid_m2", "OLS residuals, model 2")]:
    np.random.seed(SEED)
    mi = Moran(gr[col].values, w, permutations=PERM)
    rows.append(dict(variable=lab, morans_I=mi.I, expected_I=mi.EI, z_score=mi.z_sim, pseudo_p=mi.p_sim,
                     interpretation="Residuals clustered -> spatial model warranted" if mi.p_sim < 0.05 else "Residuals random"))
mt = pd.DataFrame(rows)
mt.round(4).to_csv(OUT / "spatial_global_morans_I.csv", index=False)
print(mt.round(3).to_string(index=False))

# Fig 15 - Moran's I bar chart
mm = mt[mt.variable.isin(V.ALL.values())].sort_values("morans_I")
fig, ax = plt.subplots(figsize=(10, 6.5))
colors = [style.CAT[0] if v in V.IMMIGRATION.values() else style.CAT[1] if v in V.DEMOGRAPHICS.values() else style.CAT[2]
          for v in mm.variable]
ax.barh(mm.variable, mm.morans_I, color=colors, height=0.62)
for y, (i_, p_) in enumerate(zip(mm.morans_I, mm.pseudo_p)):
    ax.text(i_ + 0.01, y, f"{i_:.2f}" + ("" if p_ < 0.05 else " (n.s.)"), va="center", fontsize=9.5, color=style.INK)
ax.axvline(0, color=style.INK2, lw=1)
ax.set_xlabel("Global Moran's I  (0 = random; 1 = perfectly clustered)")
ax.set_title("Almost every measure is spatially clustered, not randomly scattered")
ax.grid(axis="y", visible=False)
ax.legend(handles=[Patch(color=style.CAT[0], label="Immigration"), Patch(color=style.CAT[1], label="Demographics"),
                   Patch(color=style.CAT[2], label="Vulnerability (context)")], loc="lower right")
style.source_note(fig, f"Queen contiguity, row-standardized weights, {PERM} permutations; n = {len(g)} tracts. "
                       "All values shown are significant at p < 0.01 unless marked n.s.", y=-0.05)
style.save(fig, FIG / "15_morans_I_summary.png")

# Moran scatterplots for two headline variables
fig, axes = plt.subplots(1, 2, figsize=(13, 5.6))
for ax, c in zip(axes, ["pct_foreign_born", "pct_hispanic"]):
    z = (g[c] - g[c].mean()) / g[c].std()
    lag = w.sparse @ z.values
    ax.scatter(z, lag, s=26, color=style.CAT[0], alpha=0.7, edgecolor=style.SURFACE, linewidth=0.6)
    b = np.polyfit(z, lag, 1)
    xs = np.linspace(z.min(), z.max(), 20)
    ax.plot(xs, np.polyval(b, xs), color=style.CAT[1], lw=2)
    ax.axhline(0, color=style.AXIS, lw=1)
    ax.axvline(0, color=style.AXIS, lw=1)
    for (tx, ty, t) in [(0.97, 0.95, "High-High"), (0.03, 0.05, "Low-Low"), (0.97, 0.05, "High-Low"), (0.03, 0.95, "Low-High")]:
        ax.text(tx, ty, t, transform=ax.transAxes, ha="right" if tx > 0.5 else "left",
                va="top" if ty > 0.5 else "bottom", fontsize=9.5, color=style.MUTED)
    ax.set_xlabel(f"{V.ALL[c]} (standardized)")
    ax.set_ylabel("Average of neighboring tracts (spatial lag)")
    ax.set_title(f"{V.ALL[c]}: Moran's I = {morans[c].I:.2f} (p = {morans[c].p_sim:.3f})", fontsize=12)
fig.suptitle("Moran scatterplots: tracts look like their neighbors", x=0.01, ha="left", fontsize=15, fontweight="semibold")
style.source_note(fig, "Slope of the orange line = Moran's I. Points in the top-right and bottom-left quadrants drive the clustering.")
fig.tight_layout(rect=(0, 0.03, 1, 0.94))
style.save(fig, FIG / "16_moran_scatterplots.png")

# ---------------------------------------------------------------- LISA cluster maps
QUAD = {1: "High-High", 2: "Low-High", 3: "Low-Low", 4: "High-Low"}


def lisa_labels(lm, alpha=0.05):
    lab = np.array([QUAD[q] for q in lm.q], dtype=object)
    lab[lm.p_sim >= alpha] = "Not significant"
    return lab


def lisa_map(ax, labels, title):
    base_map(ax)
    g.assign(_l=labels).plot(ax=ax, color=[style.LISA_COLORS[l] for l in labels], edgecolor=style.SURFACE, linewidth=0.25)
    counts = pd.Series(labels).value_counts()
    handles = [Patch(facecolor=style.LISA_COLORS[k], label=f"{k} ({counts.get(k, 0)})") for k in style.LISA_COLORS]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.97, 0.0), fontsize=8.5, handlelength=1.2,
              borderaxespad=0.2)
    ax.set_title(title, fontsize=12)


lisa_vars = ["pct_foreign_born", "pct_hispanic", "pct_nh_asian", "median_age"]
lisa_out = g[["GEOID", "NAMELSAD"]].copy()
fig, axes = plt.subplots(2, 2, figsize=(13, 11.2))
for ax, c in zip(axes.flat, lisa_vars):
    np.random.seed(SEED)
    lm = Moran_Local(g[c].values, w, permutations=PERM, seed=SEED)
    lab = lisa_labels(lm)
    lisa_out[f"lisa_{c}"] = lab
    lisa_map(ax, lab, V.ALL[c])
map_furniture(axes.flat[0])
fig.suptitle("LISA hot spots & cold spots", x=0.01, ha="left", fontsize=17, fontweight="semibold")
fig.text(0.01, 0.935, "High-High = high-value tract surrounded by high-value neighbors (hot spot); Low-Low = cold spot; "
                      "High-Low / Low-High = outliers. p < 0.05, 999 permutations.", fontsize=10.5, color=style.INK2)
style.source_note(fig, SRC)
fig.tight_layout(rect=(0, 0.03, 1, 0.92))
style.save(fig, FIG / "17_lisa_cluster_maps.png")

# ---------------------------------------------------------------- bivariate Moran / LISA: foreign-born x vulnerability
np.random.seed(SEED)
bv = Moran_BV(g.pct_foreign_born.values, g.vuln_index.values, w, permutations=PERM)
np.random.seed(SEED)
blm = Moran_Local_BV(g.pct_foreign_born.values, g.vuln_index.values, w, permutations=PERM, seed=SEED)
blab = lisa_labels(blm)
lisa_out["bv_lisa_foreignborn_x_vuln"] = blab
lisa_out.to_csv(OUT / "spatial_lisa_clusters.csv", index=False)
pd.DataFrame([dict(x="% foreign-born", y="Vulnerability Index (neighbors)", bivariate_I=bv.I, z=bv.z_sim, pseudo_p=bv.p_sim)]
             ).round(4).to_csv(OUT / "spatial_bivariate_morans_I.csv", index=False)
print(f"Bivariate Moran's I (foreign-born x neighbors' vulnerability): {bv.I:.3f}, p={bv.p_sim:.3f}")
print("BV LISA counts:", pd.Series(blab).value_counts().to_dict())
hh = lisa_out.loc[lisa_out.bv_lisa_foreignborn_x_vuln == "High-High", "NAMELSAD"].tolist()
print("BV High-High tracts:", hh)

fig, axes = plt.subplots(1, 2, figsize=(14, 6.4))
lisa_map(axes[0], lisa_labels(Moran_Local(g.pct_foreign_born.values, w, permutations=PERM, seed=SEED)),
         "Univariate LISA: % foreign-born")
lisa_map(axes[1], blab, f"Bivariate LISA: % foreign-born × neighbors' vulnerability (I = {bv.I:.2f})")
map_furniture(axes[0])
fig.suptitle("Do immigrant hot spots overlap with vulnerable neighborhoods?", x=0.01, ha="left", fontsize=16, fontweight="semibold")
fig.text(0.01, 0.885, "Right map: High-High = tract with many immigrants whose neighbors score high on vulnerability; "
                      "High-Low = many immigrants but low-vulnerability surroundings.", fontsize=10.5, color=style.INK2)
style.source_note(fig, SRC)
fig.tight_layout(rect=(0, 0.03, 1, 0.87))
style.save(fig, FIG / "18_bivariate_lisa_immigration_vulnerability.png")
