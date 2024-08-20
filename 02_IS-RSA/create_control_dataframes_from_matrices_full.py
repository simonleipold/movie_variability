#!/usr/bin/env python
## this script creates dataframes from the full distance matrices for control matrices (age, sex)
## and saves them to a new CSV file
## The dataframes contain the distances values for each pair of subjects.

import pandas as pd
from pathlib import Path

# Load the all pairs list
data_dir = Path('/project/3011157.03/Simon/proj_2022_CABB_movie/MRI')
all_pairs_list_path = data_dir / 'all_pair_list_with_reverse.csv'
all_pairs_list = pd.read_csv(all_pairs_list_path)

# remove "sub-" from the subject names
all_pairs_list['Subject1'] = all_pairs_list['Subject1'].str.replace('sub-', '')
all_pairs_list['Subject2'] = all_pairs_list['Subject2'].str.replace('sub-', '')

# Define the directory where the similarity matrices are stored
matrix_dir = Path('/project/3011157.03/Simon/proj_2022_CABB_movie/Scripts/04_2ndLev_ISRSA/matrices')

# Directory to save the results
output_dir = Path('/project/3011157.03/Simon/proj_2022_CABB_movie/Scripts/04_2ndLev_ISRSA/dfs_control')
if not output_dir.exists():
    output_dir.mkdir(exist_ok=True)
    print(f'Created directory: {output_dir}')

# Iterate over each control variable
for con_var in ['age', 'sex']:
    # Form the file name according to the provided pattern
    matrix_filename = matrix_dir / f'Control_{con_var}.csv'
    if matrix_filename.exists():
        # Read the similarity matrix
        similarity_matrix = pd.read_csv(matrix_filename, index_col=0)
        # Convert index and columns to string with padding
        similarity_matrix.index = similarity_matrix.index.map(lambda x: f'{x:03}')
        similarity_matrix.columns = similarity_matrix.columns.map(lambda x: f'{int(x):03}')

        # Initialize a list to hold the distance data
        distance_data = []

        # Loop through each pair
        for _, row in all_pairs_list.iterrows():
            subject1_padded = row["Subject1"]
            subject2_padded = row["Subject2"]

            # Extract the distance value from the similarity matrix
            distance_value = similarity_matrix.loc[subject1_padded, subject2_padded]

            # Append the pair type, subjects, and their distance to the list
            distance_data.append([row['Pair_Type'], subject1_padded, subject2_padded, distance_value])

        # Convert the list to a DataFrame
        distance_df = pd.DataFrame(distance_data, columns=['Pair_Type', 'Subject1', 'Subject2', 'Distance'])

        # Save the results to a new CSV file
        output_file_name = output_dir / f'Control_{con_var}_df_full.csv'
        distance_df.to_csv(output_file_name, index=False)
    else:
        print(f'File not found: {matrix_filename}')
