#!/usr/bin/env python3
## this script creates dataframes from the similarity matrices 
## (upper triangle) for each movie and parcel
## and saves them to a new CSV file

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
all_pairs_list_path = data_dir / 'all_pair_list_hcp7T.csv'
all_pairs_list = pd.read_csv(all_pairs_list_path, dtype=str)

matrix_dir = (
    projpath
    / 'Scripts'
    / 'MovVar_ImagNeuro_Revision01'
    / 'HCP_movie-watching'
    / 'matrices'
)

output_dir = (
    projpath
    / 'Scripts'
    / 'MovVar_ImagNeuro_Revision01'
    / 'HCP_movie-watching'
    / 'dataframes'
)

if not output_dir.exists():
    output_dir.mkdir(exist_ok=True)
    print(f'Created directory: {output_dir}')

# ------------------------------------------------------------------
# iterate over each movie and parcel
# ------------------------------------------------------------------
for movie in range(1, num_movies + 1):
    for node in range(1, num_nodes + 1):

        matrix_filename = matrix_dir / f'ISC_movie{movie}_parcel{node}.csv'

        if matrix_filename.exists():
            similarity_matrix = pd.read_csv(matrix_filename, index_col=0, dtype=str)
            similarity_matrix = similarity_matrix.apply(pd.to_numeric)

            similarity_matrix.index = similarity_matrix.index.astype(str)
            similarity_matrix.columns = similarity_matrix.columns.astype(str)

            correlation_data = []

            for _, row in all_pairs_list.iterrows():
                s1 = str(row["Subject1"])
                s2 = str(row["Subject2"])

                corr = similarity_matrix.loc[s1, s2]
                correlation_data.append([s1, s2, corr])

            correlation_df = pd.DataFrame(
                correlation_data,
                columns=['Subject1', 'Subject2', 'Correlation']
            )

            output_file_name = output_dir / f'ISCdf_upper_movie{movie}_parcel{node}.csv'
            correlation_df.to_csv(output_file_name, index=False)

        else:
            print(f'File not found: {matrix_filename}')