"""Part 1b - non-spatial statistics across Fairfax County's census tracts.

Outputs: figures/07-10_*.png, outputs/tract_*.csv
Usage  : python -P scripts/03_tract_stats.py <project_root>
"""
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, str(Path(__file__).resolve().parent))
import style
import vars as V

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
FIG, OUT, PROC = ROOT / "figures", ROOT / "outputs", ROOT / "data/processed"
style.apply()

g = gpd.read_file(PROC / "fairfax_tracts.gpkg", layer="tracts")
d = g[~g.low_pop_flag].copy()  # drop 3 near-empty tracts (<500 people)
miss = d[d[list(V.ALL)].isna().any(axis=1)]
print("dropping tracts with missing values:", list(miss.NAMELSAD))
d = d.drop(miss.index)
print(f"analysis tracts: {len(d)} (dropped {g.low_pop_flag.sum()} low-population tracts + {len(miss)} with missing data)")

# ---------------------------------------------------------------- summary table
cols = list(V.ALL)
summ = d[cols].describe(percentiles=[0.25, 0.5, 0.75]).T
summ.insert(0, "variable", [V.ALL[c] for c in summ.index])
summ["IQR"] = summ["75%"] - summ["25%"]
summ = summ.rename(columns={"25%": "Q1", "50%": "median", "75%": "Q3"})
summ.round(2).to_csv(OUT / "tract_summary_statistics.csv", index=False)
print(summ.round(1).to_string(index=False))

top = d.nlargest(10, "pct_foreign_born")[["NAMELSAD", "pop_total", "pct_foreign_born", "pct_noncitizen",
                                          "pct_hispanic", "pct_nh_asian", "vuln_index", "vuln_category"]]
top.round(1).to_csv(OUT / "tract_top10_foreign_born.csv", index=False)

# ---------------------------------------------------------------- Fig 07 histograms (small multiples)
hist_vars = list(V.IMMIGRATION) + list(V.DEMOGRAPHICS)
fig, axes = plt.subplots(3, 4, figsize=(15, 9.5))
for ax, c in zip(axes.flat, hist_vars):
    x = d[c].dropna()
    ax.hist(x, bins=22, color=style.CAT[0], edgecolor=style.SURFACE, linewidth=0.8)
    ax.axvline(x.median(), color=style.INK, lw=1.2, ls="--")
    ax.set_title(V.ALL[c], fontsize=11.5)
    ax.text(0.97, 0.93, f"median {x.median():.1f}\nrange {x.min():.0f}–{x.max():.0f}", transform=ax.transAxes,
            ha="right", va="top", fontsize=9, color=style.INK2)
    ax.grid(axis="x", visible=False)
    ax.tick_params(labelsize=9)
for ax in axes.flat[len(hist_vars):]:
    ax.axis("off")
fig.suptitle(f"How immigration and demographics vary across Fairfax County's {len(d)} census tracts",
             x=0.01, ha="left", fontsize=15, fontweight="semibold", color=style.INK)
fig.text(0.01, 0.945, "Each bar counts tracts; dashed line = median tract.", fontsize=10.5, color=style.INK2)
fig.tight_layout(rect=(0, 0.02, 1, 0.94))
style.source_note(fig, "Source: ACS 2017-2021 5-year (B05002, B03002, B01001, B01002), census tracts in Fairfax County, VA.")
style.save(fig, FIG / "07_tract_distributions.png")

# ---------------------------------------------------------------- Fig 08 correlation heatmap
corr = d[cols].corr(method="pearson")
n = len(d)
pvals = pd.DataFrame(np.ones_like(corr), index=cols, columns=cols)
for i in cols:
    for j in cols:
        if i != j:
            pvals.loc[i, j] = stats.pearsonr(d[i], d[j], alternative="two-sided").pvalue
corr.round(3).to_csv(OUT / "tract_correlations.csv")
div = LinearSegmentedColormap.from_list("div", ["#184f95", "#6da7ec", "#f0efec", "#ec8a88", "#a52a2a"])
labels = [V.ALL[c] for c in cols]
fig, ax = plt.subplots(figsize=(11.5, 9.5))
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
m = np.ma.array(corr.values, mask=mask)
im = ax.imshow(m, cmap=div, vmin=-1, vmax=1)
for i in range(len(cols)):
    for j in range(i + 1):
        v = corr.values[i, j]
        star = "" if i == j or pvals.values[i, j] < 0.05 else "ⁿˢ"
        ax.text(j, i, f"{v:.2f}{star}", ha="center", va="center", fontsize=8.5,
                color="white" if abs(v) > 0.6 else style.INK)
ax.set_xticks(range(len(cols)), labels, rotation=45, ha="right", fontsize=9.5)
ax.set_yticks(range(len(cols)), labels, fontsize=9.5)
ax.grid(False)
for s_ in ax.spines.values():
    s_.set_visible(False)
cb = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.02)
cb.set_label("Pearson r", color=style.INK2)
cb.outline.set_visible(False)
ax.set_title("Immigrant-heavy tracts are more Hispanic, younger, and more vulnerable")
style.source_note(fig, f"n = {n} tracts. ⁿˢ = not significant at p < 0.05. Source: ACS 2017-2021 5-year; Fairfax County Vulnerability Index 2021.", y=-0.07)
style.save(fig, FIG / "08_correlation_heatmap.png")

# ---------------------------------------------------------------- OLS regressions
def ols(y, X):
    Xc = sm.add_constant(d[X])
    return sm.OLS(d[y], Xc).fit()

m1 = ols("vuln_index", ["pct_foreign_born"])
X2 = ["pct_noncitizen", "pct_nh_asian", "pct_nh_black", "pct_hispanic", "pct_under18", "pct_65plus"]
m2 = ols("vuln_index", X2)
vif = pd.DataFrame({"variable": X2,
                    "VIF": [variance_inflation_factor(sm.add_constant(d[X2]).values, i + 1) for i in range(len(X2))]})
with open(OUT / "tract_regression.txt", "w", encoding="utf-8") as f:
    f.write("MODEL 1: Vulnerability Index ~ % foreign-born\n")
    f.write(m1.summary().as_text())
    f.write("\n\nMODEL 2: Vulnerability Index ~ immigration + race/ethnicity + age\n")
    f.write(m2.summary().as_text())
    f.write("\n\nVariance inflation factors (model 2; < 5 is fine, > 10 is a problem):\n")
    f.write(vif.round(2).to_string(index=False))
coef = pd.DataFrame({"model": ["M1"] * len(m1.params) + ["M2"] * len(m2.params),
                     "term": list(m1.params.index) + list(m2.params.index),
                     "coef": list(m1.params) + list(m2.params),
                     "std_err": list(m1.bse) + list(m2.bse),
                     "p_value": list(m1.pvalues) + list(m2.pvalues)})
coef.round(4).to_csv(OUT / "tract_regression_coefficients.csv", index=False)
print(f"M1: R2={m1.rsquared:.3f}, b={m1.params.iloc[1]:.4f}, p={m1.pvalues.iloc[1]:.2g}")
print(f"M2: R2={m2.rsquared:.3f}, adjR2={m2.rsquared_adj:.3f}")
print(coef[coef.model == "M2"].round(4).to_string(index=False))
print(vif.round(2).to_string(index=False))

# residuals for the spatial script
d[["GEOID"]].assign(resid_m1=m1.resid.values, resid_m2=m2.resid.values).to_csv(PROC / "ols_residuals.csv", index=False)

# ---------------------------------------------------------------- Fig 09 scatter: foreign-born vs vulnerability
r, p = stats.pearsonr(d.pct_foreign_born, d.vuln_index)
fig, ax = plt.subplots(figsize=(10, 6.2))
ax.scatter(d.pct_foreign_born, d.vuln_index, s=34, color=style.CAT[0], alpha=0.75, edgecolor=style.SURFACE, linewidth=0.8)
xs = np.linspace(d.pct_foreign_born.min(), d.pct_foreign_born.max(), 50)
ax.plot(xs, m1.params.iloc[0] + m1.params.iloc[1] * xs, color=style.CAT[1], lw=2)
ax.text(0.02, 0.96, f"r = {r:.2f}   R² = {m1.rsquared:.2f}   p < 0.001\n"
                    f"+10 pts foreign-born → +{10 * m1.params.iloc[1]:.2f} on the index",
        transform=ax.transAxes, va="top", fontsize=10.5, color=style.INK)
ax.set_xlabel("% of tract residents who are foreign-born")
ax.set_ylabel("Vulnerability Index (1 = very low, 5 = very high)")
ax.set_title("Tracts with more immigrants score higher on Fairfax's Vulnerability Index")
style.source_note(fig, f"n = {len(d)} tracts; orange line = OLS fit. Note: the index includes limited-English share, "
                       "so part of this link is built in.", y=-0.04)
style.save(fig, FIG / "09_scatter_foreignborn_vs_vulnerability.png")

# ---------------------------------------------------------------- Fig 10 regression coefficient plot (standardized)
z = d[X2 + ["vuln_index"]].apply(lambda s: (s - s.mean()) / s.std())
ms = sm.OLS(z.vuln_index, sm.add_constant(z[X2])).fit()
cf = pd.DataFrame({"term": X2, "beta": ms.params[X2].values, "lo": ms.conf_int().loc[X2, 0].values,
                   "hi": ms.conf_int().loc[X2, 1].values, "p": ms.pvalues[X2].values}).sort_values("beta")
fig, ax = plt.subplots(figsize=(10, 5))
yy = np.arange(len(cf))
cols_ = [style.CAT[0] if p_ < 0.05 else style.AXIS for p_ in cf.p]
ax.hlines(yy, cf.lo, cf.hi, color=cols_, lw=2.2)
ax.scatter(cf.beta, yy, s=70, color=cols_, zorder=3, edgecolor=style.SURFACE, linewidth=1.5)
ax.axvline(0, color=style.INK2, lw=1)
ax.set_yticks(yy, [V.ALL[t] for t in cf.term])
for y_, b, p_ in zip(yy, cf.beta, cf.p):
    ax.text(b, y_ + 0.25, f"β={b:.2f}" + ("" if p_ < 0.05 else " (n.s.)"), ha="center", fontsize=9, color=style.INK2)
ax.set_xlabel("Standardized coefficient (change in index SDs per 1-SD increase), 95% CI")
ax.set_title(f"What predicts tract vulnerability? (Model 2, R² = {m2.rsquared:.2f})")
ax.grid(axis="y", visible=False)
style.source_note(fig, "OLS on standardized variables; blue = significant at p < 0.05, gray = not significant.", y=-0.06)
style.save(fig, FIG / "10_regression_coefficients.png")
