# IS-RSA Analysis

Run the scripts in the following order.

| Step | Script | Notes |
| --- | --- | --- |
| 1 | `create_is-distance_matrices.py` | Submit to the cluster with `submit_create_is-distance_matrices.py`. |
| 2a | `create_neural_dataframes_from_matrices_upper.py` | Submit to the cluster with `submit_create_neural_dataframes.py`. |
| 2b | `create_neural_dataframes_from_matrices_full.py` | Submit to the cluster with `submit_create_neural_dataframes.py`. |
| 3 | `create_behavioral_matrices.py` | Create behavioral distance matrices. |
| 4a | `create_behavioral_dataframes_from_matrices_upper.py` | Create upper-triangle behavioral dataframes. |
| 4b | `create_behavioral_dataframes_from_matrices_full.py` | Create full behavioral dataframes. |
| 5 | `create_control_matrices.py` | Create control matrices. |
| 6a | `create_control_dataframes_from_matrices_upper.py` | Create upper-triangle control dataframes. |
| 6b | `create_control_dataframes_from_matrices_full.py` | Create full control dataframes. |
| 7 | `Movie_ISRSA_2024_07_01.R` | Run the IS-RSA analysis. |
| 8 | `visualize_movie_ISRSA_results.py` | Visualize IS-RSA results. |
| 9 | `format_ISRSA_results.py` | Format final IS-RSA outputs. |
