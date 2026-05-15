#!/usr/bin/env python
"""
Create long-format neural distance dataframes from the upper-triangle
subject-by-subject correlation-distance matrices for each movie and
Schaefer parcel.

Each output CSV contains the neural distance value for each unique
subject pair.
"""

import pandas as pd
from pathlib import Path


# ------------------------------------------------------------------
# settings
# ------------------------------------------------------------------
num_nodes = 300  # Schaefer 2018: 300 parcels
num_movies = 8   # CABB: 8 movies


# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
project_dir = Path("/project/3011157.03/Simon/proj_2022_CABB_movie")
data_dir = project_dir / "MRI"

main_out_dir = (
    project_dir
    / "Scripts"
    / "MovVar_ImagNeuro_Revision01"
    / "CABB_Schaefer"
)

matrix_dir = main_out_dir / "matrices_distance"
output_dir = main_out_dir / "dfs_neural"

output_dir.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------
# helper
# ------------------------------------------------------------------
def clean_subject_id(x):
    """
    Convert subject IDs to 3-digit strings.

    Handles:
    - 'sub-001'
    - '001'
    - 1
    - '1'
    """
    x = str(x).replace("sub-", "")
    return x.zfill(3)


# ------------------------------------------------------------------
# load upper-triangle all-pairs list
# ------------------------------------------------------------------
all_pairs_list_path = data_dir / "all_pair_list.csv"

all_pairs_list = pd.read_csv(
    all_pairs_list_path,
    dtype={
        "Subject1": str,
        "Subject2": str,
        "Pair_Type": str,
    },
)

all_pairs_list["Subject1"] = all_pairs_list["Subject1"].apply(clean_subject_id)
all_pairs_list["Subject2"] = all_pairs_list["Subject2"].apply(clean_subject_id)


# ------------------------------------------------------------------
# iterate over movies and Schaefer parcels
# ------------------------------------------------------------------
for movie in range(1, num_movies + 1):
    print(f"\nProcessing movie {movie}")

    for node in range(1, num_nodes + 1):

        matrix_filename = matrix_dir / f"movie{movie}_parcel{node}.csv"

        if not matrix_filename.exists():
            print(f"File not found: {matrix_filename}")
            continue

        # ----------------------------------------------------------
        # read distance matrix
        # ----------------------------------------------------------
        distance_matrix = pd.read_csv(matrix_filename, index_col=0)

        distance_matrix.index = distance_matrix.index.map(clean_subject_id)
        distance_matrix.columns = distance_matrix.columns.map(clean_subject_id)

        # ----------------------------------------------------------
        # extract upper-triangle pairwise neural distance values
        # ----------------------------------------------------------
        distance_data = []

        for _, row in all_pairs_list.iterrows():
            subject1 = row["Subject1"]
            subject2 = row["Subject2"]

            try:
                distance_value = distance_matrix.loc[subject1, subject2]
            except KeyError:
                raise KeyError(
                    f"Subject pair not found in matrix {matrix_filename}: "
                    f"{subject1}, {subject2}"
                )

            distance_data.append(
                [
                    row["Pair_Type"],
                    subject1,
                    subject2,
                    distance_value,
                ]
            )

        # ----------------------------------------------------------
        # save long-format dataframe
        # ----------------------------------------------------------
        distance_df = pd.DataFrame(
            distance_data,
            columns=[
                "Pair_Type",
                "Subject1",
                "Subject2",
                "Distance",
            ],
        )

        output_file_name = output_dir / f"df_upper_movie{movie}_parcel{node}.csv"
        distance_df.to_csv(output_file_name, index=False)

print("\nFinished creating upper-triangle neural distance dataframes.")