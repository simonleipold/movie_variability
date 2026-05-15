# Head-Motion Control Analysis

This control analysis tests whether movie effects in ISC remain after accounting for participant head motion.

Run the scripts in the following order.

| Step | Script | Notes |
| --- | --- | --- |
| 1 | `motion_movies_2026_05_04.R` | Extract mean framewise displacement per participant and movie, summarize motion, and run a repeated-measures ANOVA on framewise displacement. |
| 2 | `isc_movie_comparison_2026_05_04.R` | Residualize ISC values by pairwise average framewise displacement and run parcel-wise repeated-measures ANOVAs across movies. |
| 3 | `visualize_anova.py` | Visualize the framewise-displacement-adjusted ISC ANOVA results. |
