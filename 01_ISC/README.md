# ISC Analysis

Run the scripts in the following order.

| Step | Script | Notes |
| --- | --- | --- |
| 1 | `create_movies_mask.py` | Create movie masks. |
| 2 | `extract_timeseries.py` | Submit to the cluster with `submit_extract_timeseries.py`. |
| 3 | `create_isc_matrices.py` | Submit to the cluster with `submit_create_isc_matrices.py`. |
| 4a | `create_pairlist_real_pseudo.py` | Create real/pseudo pair lists. |
| 4b | `create_pairlist_real_pseudo_with_reverse.py` | Create pair lists including reversed pairs. |
| 5a | `create_dataframes_from_matrices_upper.py` | Submit to the cluster with `submit_create_dataframes.py`. |
| 5b | `create_dataframes_from_matrices_full.py` | Submit to the cluster with `submit_create_dataframes.py`. |
| 6 | `isc_movie_comparison.R` | Compare ISC values across movies. |
| 7 | `visualize_anova.py` | Visualize ANOVA results. |
