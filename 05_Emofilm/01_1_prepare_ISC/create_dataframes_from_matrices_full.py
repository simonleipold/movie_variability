#!/usr/bin/env python3
## this script creates dataframes from the full similarity matrices for each movie and parcel
## and saves them to a new CSV file
## The dataframes contain the correlation values for each pair of subjects.

import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# settings
# ------------------------------------------------------------------
num_nodes = 210   # 210 cortical parcels of the Brainnetome atlas
num_movies = 14   # 14 Emofilm clips

# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
projpath = Path('/project/3011157.03/Simon/proj_2022_CABB_movie')

data_dir = projpath / 'MRI'
all_pairs_list_path = data_dir / 'all_pair_list_with_reverse_emofilm.csv'
all_pairs_list = pd.read_csv(all_pairs_list_path, dtype=str)

matrix_dir = (
    projpath
    / 'Scripts'
    / 'MovVar_ImagNeuro_Revision01'
    / 'Emofilm'
    / 'matrices'
)

output_dir = (
    projpath
    / 'Scripts'
    / 'MovVar_ImagNeuro_Revision01'
    / 'Emofilm'
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
            # read similarity matrix
            similarity_matrix = pd.read_csv(matrix_filename, index_col=0)

            # convert matrix values back to numeric
            similarity_matrix = similarity_matrix.apply(pd.to_numeric)

            # make sure row/column names are strings
            similarity_matrix.index = similarity_matrix.index.astype(str)
            similarity_matrix.columns = similarity_matrix.columns.astype(str)

            # initialize list to hold pairwise correlations
            correlation_data = []

            # loop through each pair
            for _, row in all_pairs_list.iterrows():
                subject1 = str(row["Subject1"])
                subject2 = str(row["Subject2"])

                correlation_value = similarity_matrix.loc[subject1, subject2]
                correlation_data.append([subject1, subject2, correlation_value])

            # convert to dataframe
            correlation_df = pd.DataFrame(
                correlation_data,
                columns=['Subject1', 'Subject2', 'Correlation']
            )

            # save output
            output_file_name = output_dir / f'ISCdf_full_movie{movie}_parcel{node}.csv'
            correlation_df.to_csv(output_file_name, index=False)

        else:
            print(f'File not found: {matrix_filename}')