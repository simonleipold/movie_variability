# Equal-Length Control Analysis

This control analysis repeats the ISC/ANOVA and IS-RSA workflows using movies with equalized lengths.

## Part I: ISC and ANOVA

Run the scripts in the following order.

| Step | Script | Notes |
| --- | --- | --- |
| 1 | `create_isc_matrices_CONTROL_length.py` | Submit to the cluster with `submit_create_isc_matrices_CONTROL_length.py`. |
| 2a | `create_dataframes_from_matrices_upper_CONTROL_length.py` | Submit to the cluster with `submit_create_dataframes_CONTROL_length.py`. |
| 2b | `create_dataframes_from_matrices_full_CONTROL_length.py` | Submit to the cluster with `submit_create_dataframes_CONTROL_length.py`. |
| 3 | `isc_movie_comparison.R` | Compare ISC values across movies. |
| 4 | `visualize_anova_CONTROL_length.py` | Visualize ANOVA results. |

## Part II: IS-RSA

Run the scripts in the following order.

| Step | Script | Notes |
| --- | --- | --- |
| 1 | `create_is-distance_matrices_CONTROL_length.py` | Submit to the cluster with `submit_create_is-distance_matrices.py`. |
| 2a | `create_neural_dataframes_from_matrices_upper_CONTROL_length.py` | Submit to the cluster with `submit_create_neural_dataframes_CONTROL_length.py`. |
| 2b | `create_neural_dataframes_from_matrices_full_CONTROL_length.py` | Submit to the cluster with `submit_create_neural_dataframes_CONTROL_length.py`. |
| 3 | `create_behavioral_matrices_CONTROL_length.py` | Create behavioral distance matrices. |
| 4a | `create_behavioral_dataframes_from_matrices_upper_CONTROL_length.py` | Create upper-triangle behavioral dataframes. |
| 4b | `create_behavioral_dataframes_from_matrices_full_CONTROL_length.py` | Create full behavioral dataframes. |
| 5 | `create_control_matrices_CONTROL_length.py` | Create control matrices. |
| 6a | `create_control_dataframes_from_matrices_upper_CONTROL_length.py` | Create upper-triangle control dataframes. |
| 6b | `create_control_dataframes_from_matrices_full_CONTROL_length.py` | Create full control dataframes. |
| 7 | `Movie_ISRSA_2025_05_16.R` | Run the IS-RSA analysis. |
| 8 | `visualize_movie_ISRSA_results_CONTROL_length.py` | Visualize IS-RSA results. |
| 9 | `format_ISRSA_results_CONTROL_length.py` | Format final IS-RSA outputs. |
