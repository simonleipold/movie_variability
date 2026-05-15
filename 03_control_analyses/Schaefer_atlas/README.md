# Schaefer Atlas Control Analysis

This control analysis repeats the CABB movie ISC/ANOVA and IS-RSA workflows using the Schaefer 2018 300-parcel, 17-network atlas instead of the main atlas.

## Part I: ISC and ANOVA

Run the scripts in the following order.

| Step | Script | Notes |
| --- | --- | --- |
| 1 | `01_1_prepare_ISC/resample_Schaefer.py` | Fetch the Schaefer atlas, resample it to the analysis space, save labels, and create QC outputs. |
| 2 | `01_1_prepare_ISC/extract_timeseries.py` | Submit to the cluster with `01_1_prepare_ISC/submit_extract_timeseries.py`. |
| 3 | `01_1_prepare_ISC/create_isc_matrices.py` | Submit to the cluster with `01_1_prepare_ISC/submit_create_isc_matrices.py`. |
| 4a | `01_1_prepare_ISC/create_dataframes_from_matrices_upper.py` | Submit to the cluster with `01_1_prepare_ISC/submit_create_dataframes.py`. |
| 4b | `01_1_prepare_ISC/create_dataframes_from_matrices_full.py` | Submit to the cluster with `01_1_prepare_ISC/submit_create_dataframes.py`. |
| 5 | `isc_movie_comparison_2025_05_10.R` | Compare ISC values across movies using the Schaefer atlas. |
| 6 | `01_2_post_ISC/visualize_anova.py` | Visualize ANOVA results. |

## Part II: IS-RSA

Run the scripts in the following order.

| Step | Script | Notes |
| --- | --- | --- |
| 1 | `02_1_prepare_ISRSA/create_is-distance_matrices.py` | Submit to the cluster with `02_1_prepare_ISRSA/submit_create_is-distance_matrices.py`. |
| 2a | `02_1_prepare_ISRSA/create_neural_dataframes_from_matrices_upper.py` | Submit to the cluster with `02_1_prepare_ISRSA/submit_create_neural_dataframes.py`. |
| 2b | `02_1_prepare_ISRSA/create_neural_dataframes_from_matrices_full.py` | Submit to the cluster with `02_1_prepare_ISRSA/submit_create_neural_dataframes.py`. |
| 3 | `Movie_ISRSA_2026_05_10_CABB_Schaefer.R` | Run the IS-RSA analysis using Schaefer atlas outputs. |
| 4 | `02_2_post_ISRSA/visualize_movie_ISRSA_results.py` | Visualize IS-RSA results. |
| 5 | `02_2_post_ISRSA/format_ISRSA_results.py` | Format final IS-RSA outputs. |
| 6 | `02_2_post_ISRSA/correlate_ISRSA_maps.py` | Correlate IS-RSA maps across movies. |
