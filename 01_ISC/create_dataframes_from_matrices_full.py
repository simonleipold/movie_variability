#!/usr/bin/env python
## this script creates dataframes from the full similarity matrices for each movie and parcel
## and saves them to a new CSV file
## The dataframes contain the correlation values for each pair of subjects.

import pandas as pd
from pathlib import Path

# Define the range for nodes
num_nodes = 210 # 210 cortical parcels of the Brainnetome atlas
num_movies = 8 # 8 movies

# Load the all pairs list
data_dir = Path('/project/3011157.03/Simon/proj_2022_CABB_movie/MRI')
all_pairs_list_path = data_dir / 'all_pair_list_with_reverse.csv'
all_pairs_list = pd.read_csv(all_pairs_list_path)

# remove "sub-" from the subject names
all_pairs_list['Subject1'] = all_pairs_list['Subject1'].str.replace('sub-', '')
all_pairs_list['Subject2'] = all_pairs_list['Subject2'].str.replace('sub-', '')

# Define the directory where the similarity matrices are stored
matrix_dir = Path('/project/3011157.03/Simon/proj_2022_CABB_movie/Scripts/03_2ndLev_ISC/matrices')

# Directory to save the results
output_dir = Path('/project/3011157.03/Simon/proj_2022_CABB_movie/Scripts/03_2ndLev_ISC/dataframes')
if not output_dir.exists():
    output_dir.mkdir(exist_ok=True)
    print(f'Created directory: {output_dir}')

# Iterate over each movie and node
for movie in range(1, num_movies + 1):
    for node in range(1, num_nodes + 1):
        # Form the file name according to the provided pattern
        matrix_filename = matrix_dir / f'ISC_movie{movie}_parcel{node}.csv'
        if matrix_filename.exists():
            # Read the similarity matrix
            similarity_matrix = pd.read_csv(matrix_filename, index_col=0)
            # Convert index and columns to string with padding
            similarity_matrix.index = similarity_matrix.index.map(lambda x: f'{x:03}')
            similarity_matrix.columns = similarity_matrix.columns.map(lambda x: f'{int(x):03}')

            # Initialize a list to hold the correlation data
            correlation_data = []

            # Loop through each pair
            for _, row in all_pairs_list.iterrows():
                subject1_padded = row["Subject1"]
                subject2_padded = row["Subject2"]

                # Extract the correlation value from the similarity matrix
                correlation_value = similarity_matrix.loc[subject1_padded, subject2_padded]

                # Append the pair type, subjects, and their correlation to the list
                correlation_data.append([row['Pair_Type'], subject1_padded, subject2_padded, correlation_value])

            # Convert the list to a DataFrame
            correlation_df = pd.DataFrame(correlation_data, columns=['Pair_Type', 'Subject1', 'Subject2', 'Correlation'])

            # Save the results to a new CSV file
            output_file_name = output_dir / f'ISCdf_full_movie{movie}_parcel{node}.csv'
            correlation_df.to_csv(output_file_name, index=False)
        else:
            print(f'File not found: {matrix_filename}')
