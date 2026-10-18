"""Part 1a - non-geospatial, county-level analysis of Fairfax's multiracial population.

Inputs : data/raw/B05002_multiracial_2021.csv  (ACS 2017-2021 5-yr, place of birth by nativity/citizenship)
         data/raw/S0201_multiracial_2024.csv   (ACS 2024 1-yr, selected population profile)
Outputs: figures/01_*.png ... figures/06_*.png, outputs/county_*.csv
Usage  : python -P scripts/01_county_descriptive.py <project_root>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import style

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
RAW, FIG, OUT = ROOT / "data/raw", ROOT / "figures", ROOT / "outputs"
style.apply()
Z90 = 1.645


def num(v):
    """Parse ACS cell text ('87,211', '±3,693', '92.2%') to float; NaN for (X)/N/-."""
    if pd.isna(v):
        return np.nan
    s = str(v).replace(",", "").replace("±", "").replace("%", "").strip()
    try:
        return float(s)
    except ValueError:
        return np.nan


def load_acs(path):
    """Return (labels, est, moe) where est/moe are DataFrames indexed by data-row number, columns = group."""
    df = pd.read_csv(path, dtype=str)
    labels = df.iloc[:, 0].str.strip()
    est, moe = {}, {}
    for col in df.columns[1:]:
        _, group, kind = col.split("!!")
        (est if kind == "Estimate" else moe)[group] = df[col].map(num)
    return labels, pd.DataFrame(est), pd.DataFrame(moe)


def prop(x, mx, y, my):
    """Census-approved proportion x/y and its 90% MOE (in percentage points)."""
    p = x / y
    rad = mx**2 - p**2 * my**2
    rad = np.where(rad < 0, mx**2 + p**2 * my**2, rad)
    return 100 * p, 100 * np.sqrt(rad) / y


def ztest(name, g1, e1, m1, g2, e2, m2, source):
    se = np.sqrt((m1 / Z90) ** 2 + (m2 / Z90) ** 2)
    z = (e1 - e2) / se
    return dict(measure=name, source=source, group_1=g1, est_1=round(e1, 1), moe_1=round(m1, 1),
                group_2=g2, est_2=round(e2, 1), moe_2=round(m2, 1), difference=round(e1 - e2, 1),
                z=round(z, 2), significant_90pct="Yes" if abs(z) > Z90 else "No")


# --------------------------------------------------------------------------- B05002 (2021)
lab21, E, M = load_acs(RAW / "B05002_multiracial_2021.csv")
R = dict(total=0, native=1, born_va=2, born_other_state=3, born_abroad_native=8, foreign=12,
         naturalized=13, nat_regions=range(14, 20), noncitizen=20, non_regions=range(21, 27))
REGIONS = ["Europe", "Asia", "Africa", "Oceania", "Latin America", "Northern America"]

short = {
    "Two or More Races": "All multiracial",
    "Two races with Some Other Race": "Two races, incl. Some Other Race",
    "Two races without Some Other Race": "Two races, excl. Some Other Race",
    "White; Black or African American": "White + Black",
    "White; American Indian and Alaska Native": "White + AIAN",
    "White; Asian": "White + Asian",
    "White; Some Other Race": "White + Some Other Race",
    "Black or African American; Asian": "Black + Asian",
    "Black or African American; Some Other Race": "Black + Some Other Race",
    "Asian; Some Other Race": "Asian + Some Other Race",
    "Three or more races with Some Other Race": "3+ races, incl. SOR",
    "Three or more races without Some Other Race": "3+ races, excl. SOR",
}
detail = ["White; Black or African American", "White; American Indian and Alaska Native", "White; Asian",
          "White; Some Other Race", "Black or African American; Asian",
          "Black or African American; Some Other Race", "Asian; Some Other Race",
          "Three or more races with Some Other Race", "Three or more races without Some Other Race"]

rows = []
for g in E.columns:
    t, mt = E.at[R["total"], g], M.at[R["total"], g]
    row = {"group": g, "total_pop": t, "total_moe": mt}
    for key in ["native", "born_va", "born_other_state", "born_abroad_native", "foreign", "naturalized", "noncitizen"]:
        p, mp = prop(E.at[R[key], g], M.at[R[key], g], t, mt)
        row[f"pct_{key}"], row[f"pct_{key}_moe"] = float(p), float(mp)
    fb, mfb = E.at[R["foreign"], g], M.at[R["foreign"], g]
    p, mp = prop(E.at[R["noncitizen"], g], M.at[R["noncitizen"], g], fb, mfb)
    row["pct_of_foreignborn_noncitizen"], row["pct_of_foreignborn_noncitizen_moe"] = float(p), float(mp)
    for i, reg in enumerate(REGIONS):
        n = E.at[R["nat_regions"][i], g] + E.at[R["non_regions"][i], g]
        row[f"fb_region_{reg}"] = 100 * n / fb if fb else np.nan
    rows.append(row)
b21 = pd.DataFrame(rows)
b21.round(2).to_csv(OUT / "county_B05002_2021_summary.csv", index=False)

# Fig 01 - % foreign-born by multiracial subgroup, with 90% MOE whiskers
d = b21[b21.group.isin(detail)].copy()
d["label"] = d.group.map(short) + "  (n≈" + (d.total_pop / 1000).round(1).astype(str) + "k)"
d = d.sort_values("pct_foreign")
overall = b21.set_index("group").at["Two or More Races", "pct_foreign"]
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(d.label, d.pct_foreign, color=style.CAT[0], height=0.62)
ax.errorbar(d.pct_foreign, d.label, xerr=d.pct_foreign_moe, fmt="none", ecolor=style.INK2, elinewidth=1.2, capsize=3)
ax.axvline(overall, color=style.INK2, ls="--", lw=1)
ax.text(overall + 0.6, -0.75, f"All multiracial residents: {overall:.1f}%", color=style.INK2, fontsize=9.5)
ax.set_ylim(-1.1, len(d) - 0.5)
for y, (v, m) in enumerate(zip(d.pct_foreign, d.pct_foreign_moe)):
    ax.text(v + m + 0.8, y, f"{v:.0f}%", va="center", fontsize=9.5, color=style.INK)
ax.set_xlabel("Share born outside the U.S. (foreign-born), %")
ax.set_title("Multiracial residents who include 'Some Other Race' are far more likely to be immigrants")
ax.grid(axis="y", visible=False)
ax.set_xlim(0, max(d.pct_foreign + d.pct_foreign_moe) + 8)
style.source_note(fig, "Source: ACS 2017-2021 5-year, Table B05002 (Two or More Races iterations), Fairfax County, VA. "
                       "Whiskers = 90% margin of error.", y=-0.04)
style.save(fig, FIG / "01_foreignborn_by_multiracial_subgroup.png")

# Fig 02 - nativity & citizenship composition (100% stacked)
comp = ["born_va", "born_other_state", "born_abroad_native", "naturalized", "noncitizen"]
comp_lab = ["Born in Virginia", "Born in another state", "Born abroad, U.S. citizen at birth*",
            "Foreign-born, naturalized citizen", "Foreign-born, not a citizen"]
order = ["Two or More Races", "Two races with Some Other Race", "Two races without Some Other Race"] + list(d.group[::-1])
c = b21.set_index("group").loc[order]
fig, ax = plt.subplots(figsize=(11, 6.8))
left = np.zeros(len(c))
ylabels = [short[g] for g in order]
for k, (col, lab) in enumerate(zip(comp, comp_lab)):
    vals = c[f"pct_{col}"].values
    ax.barh(ylabels, vals, left=left, color=style.CAT[k], height=0.66, label=lab, edgecolor=style.SURFACE, linewidth=1.5)
    for y, (l, v) in enumerate(zip(left, vals)):
        if v >= 7:
            ax.text(l + v / 2, y, f"{v:.0f}", ha="center", va="center", fontsize=8.5, color="white" if k in (0, 1, 5, 6) else style.INK)
    left += vals
ax.invert_yaxis()
ax.axhline(2.5, color=style.AXIS, lw=1)
ax.set_xlim(0, 100)
ax.set_xlabel("% of each group's population")
ax.grid(False)
ax.set_title("Where Fairfax's multiracial residents were born, and their citizenship")
ax.legend(ncol=3, loc="upper left", bbox_to_anchor=(0, -0.09), fontsize=9.5)
style.source_note(fig, "Source: ACS 2017-2021 5-year, B05002. *Born in Puerto Rico, U.S. Island Areas, or abroad to American parent(s).", y=-0.13)
style.save(fig, FIG / "02_nativity_citizenship_composition.png")

# Fig 03 - world region of birth of foreign-born, naturalized vs not a citizen (all multiracial)
g = "Two or More Races"
nat = np.array([E.at[i, g] for i in R["nat_regions"]])
non = np.array([E.at[i, g] for i in R["non_regions"]])
reg = pd.DataFrame({"region": REGIONS, "Naturalized citizen": nat, "Not a citizen": non})
reg["total"] = reg.iloc[:, 1:].sum(axis=1)
reg = reg.sort_values("total")
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(reg.region, reg["Naturalized citizen"], color=style.CAT[0], height=0.6, label="Naturalized citizen",
        edgecolor=style.SURFACE, linewidth=1.5)
ax.barh(reg.region, reg["Not a citizen"], left=reg["Naturalized citizen"], color=style.CAT[1], height=0.6,
        label="Not a citizen", edgecolor=style.SURFACE, linewidth=1.5)
fbt = reg.total.sum()
for y, t in enumerate(reg.total):
    ax.text(t + 150, y, f"{t:,.0f}  ({100 * t / fbt:.0f}%)", va="center", fontsize=9.5, color=style.INK)
ax.set_xlabel("Foreign-born multiracial residents (people)")
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.set_title("3 in 4 foreign-born multiracial residents were born in Latin America")
ax.grid(axis="y", visible=False)
ax.set_xlim(0, reg.total.max() * 1.22)
ax.legend(loc="lower right")
style.source_note(fig, "Source: ACS 2017-2021 5-year, B05002, Two or More Races, Fairfax County.", y=-0.06)
style.save(fig, FIG / "03_region_of_birth_citizenship.png")

reg.to_csv(OUT / "county_region_of_birth_2021.csv", index=False)

# --------------------------------------------------------------------------- S0201 (2024)
lab24, E4, M4 = load_acs(RAW / "S0201_multiracial_2024.csv")
G_ALL, G_WITH, G_EXCL, G_WSOR = E4.columns
gname = {G_ALL: "All multiracial", G_WITH: "Two races incl. Some Other Race",
         G_EXCL: "Excl. Some Other Race / 3+ races", G_WSOR: "White + Some Other Race"}
L = lambda line: line - 2  # file line number -> data row
TOT = L(3)


def s(line, g):
    return E4.at[L(line), g], M4.at[L(line), g]


def share(num_line, den_line, g):
    x, mx = s(num_line, g)
    y, my = s(den_line, g)
    p, mp = prop(x, mx, y, my)
    return float(p), float(mp)


prof = {}
for g in E4.columns:
    prof[g] = {
        "Total population": s(3, g),
        "% male": s(10, g),
        "Median age (years)": s(21, g),
        "% under 18": (100 - s(22, g)[0], s(22, g)[1]),
        "% 65 and over": s(25, g),
        "% foreign-born": share(144, 3, g),
        "% not a U.S. citizen (of total pop.)": share(150, 3, g),
        "% of foreign-born who are not citizens": share(150, 144, g),
        "% of immigrants who arrived 2010 or later": s(154, g),
        "% speak a language other than English at home": s(168, g),
        "% speak English less than 'very well'": s(169, g),
        "% with no health insurance": s(271, g),
        "% bachelor's degree or higher (25+)": s(107, g),
        "Median household income ($)": s(236, g),
    }
profile = pd.DataFrame({gname[g]: {k: f"{v[0]:,.1f} ± {v[1]:,.1f}" for k, v in d_.items()} for g, d_ in prof.items()})
profile.to_csv(OUT / "county_S0201_2024_profile.csv")

# Significance tests
tests = []
for k in prof[G_WITH]:
    if k == "Total population":
        continue
    (e1, m1), (e2, m2) = prof[G_WITH][k], prof[G_EXCL][k]
    tests.append(ztest(k, gname[G_WITH], e1, m1, gname[G_EXCL], e2, m2, "S0201 2024 1-yr"))
b = b21.set_index("group")
for g1, g2 in [("Two races with Some Other Race", "Two races without Some Other Race"),
               ("White; Some Other Race", "White; Asian"),
               ("White; Asian", "White; Black or African American")]:
    tests.append(ztest("% foreign-born", short[g1], b.at[g1, "pct_foreign"], b.at[g1, "pct_foreign_moe"],
                       short[g2], b.at[g2, "pct_foreign"], b.at[g2, "pct_foreign_moe"], "B05002 2017-21 5-yr"))
g1, g2 = "Two races with Some Other Race", "Two races without Some Other Race"
tests.append(ztest("% of foreign-born who are not citizens", short[g1], b.at[g1, "pct_of_foreignborn_noncitizen"],
                   b.at[g1, "pct_of_foreignborn_noncitizen_moe"], short[g2], b.at[g2, "pct_of_foreignborn_noncitizen"],
                   b.at[g2, "pct_of_foreignborn_noncitizen_moe"], "B05002 2017-21 5-yr"))
zt = pd.DataFrame(tests)
zt.to_csv(OUT / "county_significance_tests.csv", index=False)
print(zt[["measure", "est_1", "est_2", "z", "significant_90pct"]].to_string())

# Fig 04 - immigration profile, incl. SOR vs excl. SOR (2024)
metrics = ["% foreign-born", "% of foreign-born who are not citizens", "% of immigrants who arrived 2010 or later",
           "% speak a language other than English at home", "% speak English less than 'very well'",
           "% with no health insurance"]
nice = ["Foreign-born", "Of immigrants: not a citizen", "Of immigrants: arrived 2010+",
        "Speak non-English language at home", "Speak English < 'very well'", "No health insurance"]
y = np.arange(len(metrics))
h = 0.36
fig, ax = plt.subplots(figsize=(10, 6))
for j, (g, col) in enumerate([(G_WITH, style.CAT[1]), (G_EXCL, style.CAT[0])]):
    vals = np.array([prof[g][m][0] for m in metrics])
    errs = np.array([prof[g][m][1] for m in metrics])
    pos = y - h / 2 + j * h
    ax.barh(pos, vals, height=h - 0.04, color=col, label=gname[g])
    ax.errorbar(vals, pos, xerr=errs, fmt="none", ecolor=style.INK2, elinewidth=1, capsize=2.5)
    for p_, v, e in zip(pos, vals, errs):
        ax.text(v + e + 1, p_, f"{v:.0f}%", va="center", fontsize=9, color=style.INK)
ax.set_yticks(y, nice)
ax.invert_yaxis()
ax.set_xlim(0, 100)
ax.set_xlabel("%")
ax.grid(axis="y", visible=False)
ax.set_title("Two multiracial groups with very different immigration stories (2024)")
ax.legend(loc="lower right")
style.source_note(fig, "Source: ACS 2024 1-year, S0201 Selected Population Profile, Fairfax County. Whiskers = 90% MOE.", y=-0.05)
style.save(fig, FIG / "04_immigration_profile_SOR_vs_not.png")

# Fig 05 - region of birth 2024 (all vs excl SOR, plus derived incl SOR)
reg_lines = {"Latin America": 163, "Asia": 160, "Africa": 161, "Europe": 159, "Other (Oceania, N. America)": (162, 164)}
def reg_counts(g):
    fb = E4.at[L(158), g]
    out = {}
    for k, ln in reg_lines.items():
        pct = sum(E4.at[L(x), g] for x in ln) if isinstance(ln, tuple) else E4.at[L(ln), g]
        out[k] = fb * pct / 100
    return out
ca, ce = reg_counts(G_ALL), reg_counts(G_EXCL)
cw = {k: ca[k] - ce[k] for k in ca}  # derived: incl SOR = all - excl SOR
reg24 = pd.DataFrame({gname[G_ALL]: ca, gname[G_WITH] + " (derived)": cw, gname[G_EXCL]: ce})
reg24_pct = 100 * reg24 / reg24.sum()
reg24_pct.round(1).to_csv(OUT / "county_region_of_birth_2024_pct.csv")
fig, ax = plt.subplots(figsize=(10, 4.2))
left = np.zeros(3)
labels_ = list(reg24_pct.columns)
for k, r in enumerate(reg24_pct.index):
    vals = reg24_pct.loc[r].values
    ax.barh(labels_, vals, left=left, color=style.CAT[k], height=0.6, label=r, edgecolor=style.SURFACE, linewidth=1.5)
    for yy, (l, v) in enumerate(zip(left, vals)):
        if v >= 6:
            ax.text(l + v / 2, yy, f"{v:.0f}%", ha="center", va="center", fontsize=9,
                    color="white" if k in (0, 2) else style.INK)
    left += vals
ax.invert_yaxis()
ax.set_xlim(0, 100)
ax.grid(False)
ax.set_xlabel("% of foreign-born in each group")
ax.set_title("Region of birth: Latin America vs. Asia & Africa (2024)")
ax.legend(ncol=5, loc="upper left", bbox_to_anchor=(0, -0.16), fontsize=9)
style.source_note(fig, "Source: ACS 2024 1-year, S0201. 'Derived' row = all multiracial minus excl.-SOR group (Census suppresses it directly).", y=-0.2)
style.save(fig, FIG / "05_region_of_birth_2024.png")

# Fig 06 - age structure: detailed age distribution + coarse sex-by-age pyramid
ages = ["Under 5", "5-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75+"]
fig, axes = plt.subplots(1, 2, figsize=(14, 5.6), gridspec_kw={"width_ratios": [1.35, 1]})
ax = axes[0]
x = np.arange(len(ages))
w = 0.4
for j, (g, col) in enumerate([(G_WITH, style.CAT[1]), (G_EXCL, style.CAT[0])]):
    vals = [E4.at[L(ln), g] for ln in range(12, 21)]
    ax.bar(x - w / 2 + j * w, vals, width=w - 0.04, color=col, label=f"{gname[g]} (median age {prof[g]['Median age (years)'][0]:.0f})")
ax.set_xticks(x, ages)
ax.set_ylabel("% of group")
ax.grid(axis="x", visible=False)
ax.set_title("Age distribution")
ax.legend(loc="upper right", fontsize=9)

ax = axes[1]
bins = [("Under 18", 26, 27), ("18-34", 32, 33), ("35-64", 35, 36), ("65+", 38, 39)]
yy = np.arange(len(bins))
for j, (g, col) in enumerate([(G_WITH, style.CAT[1]), (G_EXCL, style.CAT[0])]):
    tot = E4.at[TOT, g]
    male = np.array([E4.at[L(c), g] * E4.at[L(m), g] / 100 / tot * 100 for _, c, m in bins])
    fem = np.array([E4.at[L(c), g] * (100 - E4.at[L(m), g]) / 100 / tot * 100 for _, c, m in bins])
    off = -0.2 + j * 0.4
    ax.barh(yy + off, -male, height=0.38, color=col)
    ax.barh(yy + off, fem, height=0.38, color=col, alpha=0.55)
ax.set_yticks(yy, [b_[0] for b_ in bins])
ax.axvline(0, color=style.INK2, lw=1)
lim = 28
ax.set_xlim(-lim, lim)
ax.set_xticks([-25, -15, -5, 0, 5, 15, 25], ["25%", "15%", "5%", "0", "5%", "15%", "25%"])
ax.text(-lim + 0.5, 3.6, "◀ Male", color=style.INK2, fontsize=10)
ax.text(lim - 0.5, 3.6, "Female ▶", color=style.INK2, fontsize=10, ha="right")
ax.set_ylim(-0.6, 3.9)
ax.grid(axis="y", visible=False)
ax.set_title("Population pyramid (sex × age)")
fig.suptitle("The 'excl. Some Other Race' group is much younger: 35% are children aged 5-17 (2024)",
             x=0.01, ha="left", fontsize=14, fontweight="semibold", color=style.INK)
style.source_note(fig, "Source: ACS 2024 1-year, S0201. Pyramid: solid = male, faded = female; bars are % of each group's total population.", y=-0.04)
fig.tight_layout()
style.save(fig, FIG / "06_age_sex_structure_2024.png")

print(profile.to_string())
