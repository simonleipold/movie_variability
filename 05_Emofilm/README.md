# Emofilm Analysis

This folder contains the ISC/ANOVA and IS-RSA workflows for the Emofilm dataset.

## Part I: ISC and ANOVA

Run the scripts in the following order.

| Step | Script | Notes |
| --- | --- | --- |
| 1 | `01_1_prepare_ISC/create_emofilm_movies_on_offsets.py` | Create participant-wise movie timing files from BIDS event files. |
| 2 | `01_1_prepare_ISC/create_emofilm_mask.py` | Create the Emofilm group mask from preprocessed BOLD files. |
| 3 | `01_1_prepare_ISC/extract_timeseries.py` | Submit to the cluster with `01_1_prepare_ISC/submit_extract_timeseries.py`. |
| 4 | `01_1_prepare_ISC/create_isc_matrices.py` | Submit to the cluster with `01_1_prepare_ISC/submit_create_isc_matrices.py`. |
| 5 | `01_1_prepare_ISC/create_pairlists.py` | Create upper-triangle and full subject pair lists. |
| 6a | `01_1_prepare_ISC/create_dataframes_from_matrices_upper.py` | Submit to the cluster with `01_1_prepare_ISC/submit_create_dataframes.py`. |
| 6b | `01_1_prepare_ISC/create_dataframes_from_matrices_full.py` | Submit to the cluster with `01_1_prepare_ISC/submit_create_dataframes.py`. |
| 7 | `isc_movie_comparison_2026_04_26.R` | Compare ISC values across Emofilm movies. |
| 8 | `01_2_post_ISC/visualize_anova.py` | Visualize ANOVA results. |

## Part II: IS-RSA

Run the scripts in the following order.

| Step | Script | Notes |
| --- | --- | --- |
| 1 | `02_1_prepare_ISRSA/create_is-distance_matrices.py` | Submit to the cluster with `02_1_prepare_ISRSA/submit_create_is-distance_matrices.py`. |
| 2a | `02_1_prepare_ISRSA/create_neural_dataframes_from_matrices_upper.py` | Submit to the cluster with `02_1_prepare_ISRSA/submit_create_neural_dataframes.py`. |
| 2b | `02_1_prepare_ISRSA/create_neural_dataframes_from_matrices_full.py` | Submit to the cluster with `02_1_prepare_ISRSA/submit_create_neural_dataframes.py`. |
| 3 | `02_1_prepare_ISRSA/create_behavioral_matrix.py` | Create the personality distance matrix. |
| 4 | `02_1_prepare_ISRSA/create_behavioral_dataframes_from_matrices.py` | Create upper-triangle and full behavioral dataframes. |
| 5 | `Movie_ISRSA_2026_04_27_emofilm.R` | Run the Emofilm IS-RSA analysis. |
| 6 | `02_2_post_ISRSA/visualize_movie_ISRSA_results.py` | Visualize IS-RSA results. |
| 7 | `02_2_post_ISRSA/format_ISRSA_results.py` | Format final IS-RSA outputs. |
| 8 | `02_2_post_ISRSA/correlate_ISRSA_maps.py` | Correlate IS-RSA statistic maps across movies. |
