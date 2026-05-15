# HCP 7T Movie-Watching Analysis

This folder contains the ISC/ANOVA and IS-RSA workflows for the HCP 7T movie-watching dataset.

## Part I: ISC and ANOVA

Run the scripts in the following order.

| Step | Script | Notes |
| --- | --- | --- |
| 1 | `01_1_prepare_ISC/create_hcp_movies_on_offsets.py` | Create timing files for the HCP 7T movie segments. |
| 2 | `01_1_prepare_ISC/create_hcp_movies_mask.py` | Create the HCP 7T movie group mask. |
| 3 | `01_1_prepare_ISC/resample_Brainnetome.py` | Resample the Brainnetome atlas to the HCP 7T mask space. |
| 4 | `01_1_prepare_ISC/extract_timeseries.py` | Submit to the cluster with `01_1_prepare_ISC/submit_extract_timeseries.py`. |
| 5 | `01_1_prepare_ISC/create_isc_matrices.py` | Submit to the cluster with `01_1_prepare_ISC/submit_create_isc_matrices.py`. |
| 6 | `01_1_prepare_ISC/create_pairlists.py` | Create upper-triangle and full subject pair lists. |
| 7a | `01_1_prepare_ISC/create_dataframes_from_matrices_upper.py` | Submit to the cluster with `01_1_prepare_ISC/submit_create_dataframes.py`. |
| 7b | `01_1_prepare_ISC/create_dataframes_from_matrices_full.py` | Submit to the cluster with `01_1_prepare_ISC/submit_create_dataframes.py`. |
| 8 | `isc_movie_comparison_2026_04_16.R` | Compare ISC values across HCP 7T movies. |
| 9 | `01_2_post_ISC/visualize_anova.py` | Visualize ANOVA results. |

## Part II: IS-RSA

Run the scripts in the following order.

| Step | Script | Notes |
| --- | --- | --- |
| 1 | `02_1_prepare_ISRSA/create_is-distance_matrices.py` | Submit to the cluster with `02_1_prepare_ISRSA/submit_create_is-distance_matrices.py`. |
| 2a | `02_1_prepare_ISRSA/create_neural_dataframes_from_matrices_upper.py` | Submit to the cluster with `02_1_prepare_ISRSA/submit_create_neural_dataframes.py`. |
| 2b | `02_1_prepare_ISRSA/create_neural_dataframes_from_matrices_full.py` | Submit to the cluster with `02_1_prepare_ISRSA/submit_create_neural_dataframes.py`. |
| 3 | `02_1_prepare_ISRSA/create_behavioral_csv.py` | Create the HCP 7T personality CSV for included subjects. |
| 4 | `02_1_prepare_ISRSA/create_behavioral_matrix.py` | Create the personality distance matrix. |
| 5 | `02_1_prepare_ISRSA/create_behavioral_dataframes_from_matrices.py` | Create upper-triangle and full behavioral dataframes. |
| 6 | `Movie_ISRSA_2026_04_14_hcp7T.R` | Run the HCP 7T IS-RSA analysis. |
| 7 | `02_2_post_ISRSA/visualize_movie_ISRSA_results.py` | Visualize IS-RSA results. |
| 8 | `02_2_post_ISRSA/format_ISRSA_results.py` | Format final IS-RSA outputs. |
| 9 | `02_2_post_ISRSA/correlate_ISRSA_maps.py` | Correlate IS-RSA maps across movies. |
