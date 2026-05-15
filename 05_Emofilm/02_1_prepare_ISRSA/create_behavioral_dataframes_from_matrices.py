#!/usr/bin/env python3
## this script creates behavioral dataframes from the personality distance matrix
## for both the full matrix and the upper triangle (Emofilm version)

import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
projpath = Path('/project/3011157.03/Simon/proj_2022_CABB_movie')

data_dir = projpath / 'MRI'

all_pairs_full_path = data_dir / 'all_pair_list_with_reverse_emofilm.csv'
all_pairs_upper_path = data_dir / 'all_pair_list_emofilm.csv'

all_pairs_full = pd.read_csv(all_pairs_full_path, dtype=str)
all_pairs_upper = pd.read_csv(all_pairs_upper_path, dtype=str)

matrix_dir = (
    projpath
    / 'Scripts'
    / 'MovVar_ImagNeuro_Revision01'
    / 'Emofilm'
    / 'matrices_behavior'
)

output_dir = (
    projpath
    / 'Scripts'
    / 'MovVar_ImagNeuro_Revision01'
    / 'Emofilm'
    / 'dfs_behavior'
)

if not output_dir.exists():
    output_dir.mkdir(exist_ok=True)
    print(f'Created directory: {output_dir}')

# ------------------------------------------------------------------
# load personality distance matrix
# ------------------------------------------------------------------
matrix_filename = matrix_dir / 'personality_distance_matrix.csv'

if not matrix_filename.exists():
    raise FileNotFoundError(f'File not found: {matrix_filename}')

distance_matrix = pd.read_csv(matrix_filename, index_col=0)
distance_matrix = distance_matrix.apply(pd.to_numeric)

distance_matrix.index = distance_matrix.index.astype(str)
distance_matrix.columns = distance_matrix.columns.astype(str)

# ------------------------------------------------------------------
# helper function
# ------------------------------------------------------------------
def build_distance_df(pair_df, matrix):
    distance_data = []

    for _, row in pair_df.iterrows():
        s1 = str(row["Subject1"])
        s2 = str(row["Subject2"])

        dist = matrix.loc[s1, s2]
        distance_data.append([s1, s2, dist])

    return pd.DataFrame(
        distance_data,
        columns=['Subject1', 'Subject2', 'Distance']
    )

# ------------------------------------------------------------------
# full dataframe
# ------------------------------------------------------------------
distance_df_full = build_distance_df(all_pairs_full, distance_matrix)
distance_df_full.to_csv(
    output_dir / 'behavior_personality_df_full.csv',
    index=False
)

# ------------------------------------------------------------------
# upper dataframe
# ------------------------------------------------------------------
distance_df_upper = build_distance_df(all_pairs_upper, distance_matrix)
distance_df_upper.to_csv(
    output_dir / 'behavior_personality_df_upper.csv',
    index=False
)

print('Saved:')
print(output_dir / 'behavior_personality_df_full.csv')
print(output_dir / 'behavior_personality_df_upper.csv')