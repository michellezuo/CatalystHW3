"""Variable labels shared by the tract-level scripts."""

IMMIGRATION = {
    "pct_foreign_born": "% foreign-born",
    "pct_noncitizen": "% not a U.S. citizen",
    "pct_born_asia": "% born in Asia",
    "pct_born_latam": "% born in Latin America",
}
DEMOGRAPHICS = {
    "pct_hispanic": "% Hispanic/Latino",
    "pct_nh_asian": "% Asian (non-Hispanic)",
    "pct_nh_black": "% Black (non-Hispanic)",
    "pct_nh_white": "% White (non-Hispanic)",
    "median_age": "Median age (years)",
    "pct_under18": "% under 18",
    "pct_65plus": "% 65 and over",
    "pct_male": "% male",
}
CONTEXT = {"vuln_index": "Vulnerability Index (1-5)"}
ALL = {**IMMIGRATION, **DEMOGRAPHICS, **CONTEXT}
