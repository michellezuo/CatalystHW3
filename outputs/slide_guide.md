# Slide Guide: Immigration & Demographics in Fairfax County

This guide is for **your** section of the presentation (about 14 slides, roughly 10–12 minutes). For each slide it gives:
- **Figure:** the file to drop in from `figures/`
- **On the slide:** short bullets to put on screen
- **Say:** what to talk through
- **If asked:** backup answers

Every number below comes from the scripts' outputs (`outputs/results_tables.xlsx` has all of them).

> **Big framing to remember.** The analysis has two layers.
> 1. **Non-geospatial (county-level):** your two Census CSVs. They describe **Fairfax's multiracial ("Two or More Races") population only**, broken into subgroups. They can't be mapped because each is a single county-wide number.
> 2. **Geospatial (tract-level):** 270 census tracts with immigration, race/ethnicity, age and sex data (ACS 2017–2021), joined to the county's Vulnerability Index. This is what supports the choropleth maps, Moran's I, and LISA.

---

## Slide 1 — Title & roadmap
**On the slide**
- "Who Lives in Fairfax? Immigration & Demographics"
- Roadmap: County profile → Tract statistics → Maps → Spatial clustering (Moran's I, LISA) → Immigration × vulnerability

**Say:** "I'll go from the county-wide picture down to the neighborhood (census tract) level. First I describe the data without geography, then I ask *where* things are and whether they cluster."

---

## Slide 2 — Data & methods
**Figure:** none (a simple two-column table works well)

**On the slide**
| Layer | Data | Methods |
|---|---|---|
| County (non-spatial) | ACS 2017–21 5-yr **B05002** (place of birth & citizenship); ACS 2024 1-yr **S0201** (population profile), both for multiracial residents | Descriptive stats, margin-of-error z-tests |
| Tract (non-spatial) | ACS 2017–21 5-yr for 270 tracts: nativity, region of birth, race/ethnicity, age, sex | Summary stats, correlations, OLS regression |
| Tract (spatial) | Same tracts + Census tract boundaries + **Fairfax Vulnerability Index** & county boundary (Fairfax open geodata) | Choropleth maps, Global Moran's I, LISA, bivariate LISA |

**Say:**
- "ACS numbers are survey estimates, so each comes with a margin of error. I use those margins to test whether differences are real."
- "For the maps I dropped 4 tracts: 3 with almost no residents (fewer than 500) and 1 with no vulnerability score. Fairfax City and Falls Church show as holes because they are independent cities."

**If asked:** "The tract populations add up to 1,146,825 and 30.6% foreign-born, which matches the county's published totals. The tract outline also matches the county boundary file (~402 vs ~407 sq mi)."

---

## Slide 3 — Which multiracial residents are immigrants?
**Figure:** `01_foreignborn_by_multiracial_subgroup.png`

**On the slide**
- About **26.5%** of Fairfax's multiracial residents are foreign-born (2017–21)
- **White + Some Other Race: 46%** foreign-born vs **White + Asian: 14%** and **White + Black: 12%**
- The gap is statistically significant (z = 11.9, 90% confidence)
- Groups that include "Some Other Race" (SOR) stand out

**Say:**
- "'Some Other Race' is a write-in category. Many Hispanic/Latino residents write in identities like 'Salvadoran' or 'Mexican', which the Census codes as SOR. So 'White + SOR' is most likely mostly Hispanic residents, which is why it is so heavily immigrant."
- "The whiskers are margins of error. Small groups like Black + Asian (about 1,200 people) have wide whiskers, so I don't over-interpret them."

---

## Slide 4 — Nativity, citizenship & region of birth
**Figures:** `02_nativity_citizenship_composition.png` (main) + `03_region_of_birth_citizenship.png` (inset or next slide)

**On the slide**
- Among all multiracial residents: **38%** born in Virginia, **29%** in another state, **14%** naturalized citizens, **12%** non-citizens
- Two-race groups **with SOR**: **22%** naturalized + **22%** non-citizen
- Two-race groups **without SOR**: only 8% naturalized and about 5% non-citizen
- **77%** of foreign-born multiracial residents were born in **Latin America**; next is Asia at **15%**
- About half of the Latin American–born are not yet citizens

**Say:** "Immigrants in the SOR groups are also less likely to be citizens: 50% of them are non-citizens, versus 37% in the non-SOR groups, a significant difference. That suggests more recent arrival or more barriers to naturalization."

---

## Slide 5 — Two very different immigration stories (2024)
**Figures:** `04_immigration_profile_SOR_vs_not.png` + `05_region_of_birth_2024.png`

**On the slide**
- **Two races incl. SOR:** 47% foreign-born; 55% of immigrants not citizens; 70% speak a non-English language at home; 29% speak English less than "very well"; 17% uninsured
- **Excl. SOR / 3+ races:** 18% foreign-born; 25% non-citizens; 30% non-English at home; 6% limited English; 3% uninsured
- Region of birth: incl. SOR is about **97% Latin America** (derived); excl. SOR is **52% Asia, 25% Africa, 18% Latin America**
- Every gap is significant **except** year of arrival (both about 40% arrived 2010 or later, z = −0.8)

**Say:**
- "The 2024 data confirms the 2021 pattern with a newer survey."
- "The SOR group is a mostly Latin American immigrant community. The other multiracial group draws more from Asia and Africa and has much better English proficiency and insurance coverage."
- "Interestingly, both groups arrived at similar times. The difference is *where* they came from, not *when*."

**If asked about 'derived':** "The Census suppresses region of birth for the SOR group, so I calculated it as all multiracial minus the non-SOR group. Treat it as approximate."

---

## Slide 6 — Demographics: age & sex (2024)
**Figure:** `06_age_sex_structure_2024.png`

**On the slide**
- Median age: **34.2** (incl. SOR) vs **19.0** (excl. SOR), a 15-year gap (z = 6.6, significant)
- **48%** of the excl.-SOR group is under 18, and **35%** are ages 5–17
- Sex ratio is balanced in both (about 51% male); the difference is **not** significant (z = 0.3)
- 65+: 9.1% vs 4.9% (significant)

**Say:**
- "The non-SOR multiracial group is overwhelmingly kids. That fits multiracial children born to parents of different races, a 'second generation' story."
- "The SOR group looks like a working-age adult immigrant population."
- "Sex is balanced. There's no gender story at the county level, and you'll see that holds on the maps too."

---

## Slide 7 — Across all 270 tracts: how much variation?
**Figure:** `07_tract_distributions.png`

**On the slide**
- The median tract is **29.7% foreign-born**, but the range is **3% to 60%**
- % non-citizen: median 9.4%, up to 48%
- % Hispanic: median 11%, but one tract is **85%** (right-skewed, a few very concentrated tracts)
- % male is tightly bunched around 50% (except a handful of group-quarters tracts)

**Say:** "This switches to *all residents*, not just multiracial, at the neighborhood level. The skewed distributions (Hispanic, Latin American–born, non-citizen) hint that these groups are concentrated in a few places, which we test on the maps."

**If asked about outliers** (median age 85, 100% aged 65+, 93% male): "Those are tracts dominated by group quarters, for example a retirement community or a military/institutional site. They're real, but unusual."

---

## Slide 8 — What goes together? (correlations)
**Figure:** `08_correlation_heatmap.png`

**On the slide**
- % foreign-born ↔ % White non-Hispanic: **r = −0.82**
- % born in Latin America ↔ % Hispanic: **r = 0.95**; % born in Asia ↔ % Asian: **r = 0.92**
- Vulnerability Index ↔ % foreign-born **0.70**, % non-citizen **0.71**, % Hispanic **0.75**
- Vulnerability ↔ % Asian: **0.01 (no relationship)**
- Immigrant-heavy tracts are younger (median age r = −0.42)

**Say:** "The most important point here is that 'immigrant' isn't one thing. Latin American immigration tracks vulnerability strongly; Asian immigration doesn't track it at all. Lumping them together hides that."

---

## Slide 9 — Immigration & vulnerability (regression)
**Figures:** `09_scatter_foreignborn_vs_vulnerability.png` + `10_regression_coefficients.png`

**On the slide**
- Model 1: each **+10 points foreign-born → +0.51** on the 1–5 Vulnerability Index (R² = 0.50, p < 0.001)
- Average % foreign-born by vulnerability category: **Very Low 19% → Low 26% → Average 32% → High 37% → Very High 48%**
- Model 2 (R² = **0.77**), standardized effects: **% Hispanic (β 0.56)** > % non-citizen (0.34) ≈ % Black (0.32) > % 65+ (0.14) > % Asian (0.10); % under 18 is slightly negative
- All predictors have VIF < 3, so there's no multicollinearity problem

**Say:**
- "This is correlation, not causation. Immigrants don't *cause* vulnerability. The index measures income, housing cost burden, insurance and similar factors, and immigrant communities often live where those are harder."
- "One important caveat: the index includes 'speaks English less than well' as one of its components, so part of this relationship is built into the index itself."

---

## Slide 10 — MAPS: Where Fairfax's immigrants live
**Figure:** `11_maps_immigration.png`

**On the slide**
- Highest-immigrant tracts (41–60% foreign-born) form a band through the **east/central** county and the **far northwest**
- **Asian-born** residents concentrate in the **west/central** county
- **Latin American–born** residents concentrate in the **east and southeast**
- The **south and southwest** have the fewest immigrants

**Say:** "Darker blue means a higher share. Each map uses quintiles, so each color holds one-fifth of tracts. Notice the Asian-born and Latin American–born maps are almost mirror images. That's the r = −0.09 from the heatmap, shown geographically."

**Tip:** if you know the area, name neighborhoods on the slide (for example the Route 1 corridor or Annandale). Check them against Google Maps first, because the maps don't have neighborhood labels.

---

## Slide 11 — MAPS: Race, ethnicity, age & sex
**Figures:** `12_maps_race_ethnicity.png` and `13_maps_age_sex.png` (two slides, or pick the key panels)

**On the slide**
- % White non-Hispanic is highest in the **south/southwest and north**; lowest in the **east/center**
- % Black is concentrated in the **southeast**
- % Hispanic is highest in the **east, southeast, and far northwest**
- Age: older tracts in the **north** and **southwest**; % male looks like random noise

**Say:** "Race and ethnicity form clear geographic blocks. Age is patchier, and sex shows no pattern at all, which the next slide confirms with statistics."

---

## Slide 12 — Is it really clustered? Global Moran's I
**Figures:** `15_morans_I_summary.png` (main) + `16_moran_scatterplots.png` (optional backup)

**On the slide**
- Moran's I measures whether similar values sit next to each other: **0 = random, + = clustered**
- Strongest clustering: **% born in Asia (0.51)**, % Asian (0.49), % Black (0.45), % White (0.43), **% foreign-born (0.42)**
- Moderate: % non-citizen 0.39, % Latin American–born 0.37, % Hispanic 0.36; Vulnerability Index 0.40
- Weak but real: age measures (0.15–0.19)
- **% male: 0.03, not significant**, randomly distributed
- All other values have p = 0.001 (999 random permutations)

**Say (plain-English explanation of Moran's I):**
- "Imagine shuffling every tract's value randomly across the map 999 times. If the real map is far more clumped than any shuffle, the pattern is real. That's what the p-value says."
- "Neighbors here means tracts that share a border or a corner ('Queen contiguity'). On average each tract has 6 neighbors."
- On the scatterplot: "Each dot is a tract. The x-axis is its own value and the y-axis is its neighbors' average. The upward slope *is* Moran's I."

**Bonus point:** the regression residuals are also clustered (I = 0.43 for Model 1, 0.15 for Model 2, both p = 0.001). "Even after accounting for demographics, vulnerability still clusters, so a spatial regression would be a good next step."

---

## Slide 13 — Where are the hot spots? LISA cluster maps
**Figure:** `17_lisa_cluster_maps.png`

**On the slide**
- LISA (Local Moran's I) finds **where** the clusters are
- **% foreign-born:** 39 hot-spot tracts (east-center and northwest), 27 cold-spot tracts (south/southwest)
- **% Hispanic:** 31 hot spots in the **east and southeast**; 38 cold spots across the **north**
- **% Asian:** 42 hot spots in the **west**; 32 cold spots in the **southeast**
- **Median age:** older hot spots in the **north**; younger cold spots scattered

**Say:**
- "Red is a hot spot: a high tract surrounded by high neighbors. Dark blue is a cold spot: low surrounded by low. Light colors are outliers, like a high tract in a low neighborhood. Gray is not statistically significant."
- "Hispanic and Asian hot spots are on **opposite sides** of the county. Fairfax's immigrant communities are geographically distinct, not one blended population."

---

## Slide 14 — Do immigrant hot spots overlap with vulnerable neighborhoods?
**Figures:** `18_bivariate_lisa_immigration_vulnerability.png` (+ `14_map_vulnerability_index.png` for context)

**On the slide**
- Bivariate Moran's I (foreign-born × neighbors' vulnerability) = **0.27, p = 0.001**
- **33 High-High tracts:** many immigrants *and* vulnerable surroundings, concentrated in the **east-center and southeast**
- **35 Low-Low tracts:** few immigrants, low vulnerability, mostly the **north and south**
- **7 High-Low tracts:** many immigrants but *low*-vulnerability surroundings, mostly in the north-center (consistent with the Asian immigrant pattern)

**Say:**
- "The left map shows where immigrants cluster. The right map asks whether those clusters sit next to vulnerable areas."
- "In the east and southeast, yes. Those High-High tracts are where services like ESL, health access and housing help would reach the most people."
- "But the High-Low tracts show that immigration doesn't automatically mean vulnerability."

---

## Slide 15 — Key takeaways
**On the slide**
1. **About 30% of Fairfax residents are immigrants**, but they're **not evenly spread**: the foreign-born share ranges from 3% to 60% by tract, and Moran's I = 0.42.
2. **Two distinct immigrant geographies:** Asian-born residents in the west, Latin American–born residents in the east/southeast. Their hot spots barely overlap.
3. **Among multiracial residents**, the "Some Other Race" groups are mostly Latin American immigrants (47% foreign-born, 55% of them non-citizens). The other multiracial groups are young (median age 19) and mostly U.S.-born.
4. **Immigration is linked to vulnerability**, driven by Hispanic and non-citizen share rather than Asian share: R² = 0.77, bivariate I = 0.27.
5. **Sex is evenly distributed** everywhere (Moran's I is not significant), while race, ethnicity and immigration all cluster strongly.

**Say:** end with a hand-off line to your partner. "Those are the 'who' and the 'where'; now [partner] will talk about …"

---

## Slide 16 — Limitations (keep it short; good for Q&A)
- **Your CSVs cover only the multiracial population**, so they describe that group, not the whole county.
- **Different survey years and types:** 2017–21 5-year vs 2024 1-year. The multiracial count roughly doubles (87,211 → 173,561). Much of that jump likely comes from the Census Bureau's 2020 changes to how write-in race responses are coded, not just real growth.
- **Margins of error:** small subgroups (about 1,000 people) have wide error bars; tract estimates are noisier than county totals.
- **Vulnerability Index overlap:** it includes limited-English share, so part of the immigration link is built in.
- **Modifiable areal unit problem (MAUP):** results can change with different boundaries (tracts vs block groups).
- **Correlation ≠ causation**, and the OLS residuals are spatially clustered, so a spatial lag or spatial error model would be the next step.

---

## Slide 17 — Data sources (put this as your final/appendix slide)
- U.S. Census Bureau, American Community Survey 2017–2021 5-Year, Table B05002, Two or More Races iterations: https://data.census.gov/table/ACSDT5YSPT2021.B05002?g=050XX00US51059
- U.S. Census Bureau, American Community Survey 2024 1-Year, Table S0201 Selected Population Profile: https://data.census.gov/table/ACSSPP1Y2024.S0201?g=050XX00US51059
- U.S. Census Bureau, ACS 2017–2021 5-Year summary files (tract-level B05002, B03002, B01001, B01002): https://www2.census.gov/programs-surveys/acs/summary_file/2021/table-based-SF/data/5YRData/
- U.S. Census Bureau, 2021 cartographic boundary file, Virginia census tracts: https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_51_tract_500k.zip
- Fairfax County, Vulnerability Index – Census Tract 2021: https://services1.arcgis.com/ioennV6PpG5Xodq0/ArcGIS/rest/services/Vulnerability_Index_Census_Tract_2021/FeatureServer/0
- Fairfax County, County Boundary: https://services1.arcgis.com/ioennV6PpG5Xodq0/ArcGIS/rest/services/Fairfax_County_Boundary/FeatureServer
- Fairfax County Open Geospatial Data hub: https://data-fairfaxcountygis.opendata.arcgis.com/
- Analysis: Python (geopandas, PySAL/esda, statsmodels).

---

### Quick glossary (for Q&A)
- **Foreign-born:** born outside the U.S. to non-U.S.-citizen parents (includes naturalized citizens and non-citizens).
- **Choropleth:** a map shaded by value per area.
- **Quintiles:** 5 color classes with an equal number of tracts in each.
- **Global Moran's I:** one number for the whole map; is it clustered?
- **LISA:** Local Indicators of Spatial Association; *where* are the clusters?
- **Bivariate LISA:** does a tract's value of X relate to its neighbors' value of Y?
- **Queen contiguity:** neighbors share a border or a corner.
- **z-test with MOE:** SE = MOE ÷ 1.645; if |z| > 1.645 the difference is significant at 90% (the Census standard).
