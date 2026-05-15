#!/usr/bin/env python3
## this script creates dataframes from the distance matrices 
## (upper triangle) for each movie and parcel (Emofilm version)

import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# settings
# ------------------------------------------------------------------
num_nodes = 210
num_movies = 14

# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
projpath = Path('/project/3011157.03/Simon/proj_2022_CABB_movie')

data_dir = projpath / 'MRI'
all_pairs_list_path = data_dir / 'all_pair_list_emofilm.csv'
all_pairs_list = pd.read_csv(all_pairs_list_path, dtype=str)

# distance matrices
matrix_dir = (
    projpath
    / 'Scripts'
    / 'MovVar_ImagNeuro_Revision01'
    / 'Emofilm'
    / 'matrices_distance'
)

# match IS-RSA naming
output_dir = (
    projpath
    / 'Scripts'
    / 'MovVar_ImagNeuro_Revision01'
    / 'Emofilm'
    / 'dfs_neural'
)

if not output_dir.exists():
    output_dir.mkdir(exist_ok=True)
    print(f'Created directory: {output_dir}')

# ------------------------------------------------------------------
# iterate over each movie and parcel
# ------------------------------------------------------------------
for movie in range(1, num_movies + 1):
    for node in range(1, num_nodes + 1):

        matrix_filename = matrix_dir / f'movie{movie}_parcel{node}.csv'

        if matrix_filename.exists():

            distance_matrix = pd.read_csv(matrix_filename, index_col=0)
            distance_matrix = distance_matrix.apply(pd.to_numeric)

            distance_matrix.index = distance_matrix.index.astype(str)
            distance_matrix.columns = distance_matrix.columns.astype(str)

            distance_data = []

            for _, row in all_pairs_list.iterrows():
                s1 = str(row["Subject1"])
                s2 = str(row["Subject2"])

                dist = distance_matrix.loc[s1, s2]
                distance_data.append([s1, s2, dist])

            distance_df = pd.DataFrame(
                distance_data,
                columns=['Subject1', 'Subject2', 'Distance']
            )

            output_file_name = output_dir / f'df_upper_movie{movie}_parcel{node}.csv'
            distance_df.to_csv(output_file_name, index=False)

        else:
            print(f'File not found: {matrix_filename}')