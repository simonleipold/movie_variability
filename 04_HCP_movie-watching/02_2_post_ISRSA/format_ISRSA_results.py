#!/usr/bin/env python3
import os
import pandas as pd

# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
proj_path = '/project/3011157.03/Simon/proj_2022_CABB_movie'

# location of R output files
r_path = os.path.join(
    proj_path,
    'Scripts',
    'MovVar_ImagNeuro_Revision01',
    'HCP_movie-watching',
    'r_output_ISRSA'
)

# output directory for formatted tables
out_dir = os.path.join(r_path, 'formatted')
if not os.path.exists(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    print(f'Directory {out_dir} created')

# ------------------------------------------------------------------
# load Brainnetome labels
# ------------------------------------------------------------------
labels_csv = os.path.join(
    proj_path,
    'MRI',
    'Brainnetome_atlas',
    'Brainnetome_labels_cortical.csv'
)
labels_df = pd.read_csv(labels_csv)

# map Yeo 7-network codes to names
network_mapping = {
    0: "NA",
    1: "Visual",
    2: "Somatomotor",
    3: "Dorsal Attention",
    4: "Ventral Attention",
    5: "Limbic",
    6: "Frontoparietal",
    7: "Default"
}
labels_df['Yeo_7network'] = labels_df['Yeo_7network'].replace(network_mapping)

# ------------------------------------------------------------------
# movies
# ------------------------------------------------------------------
movie_list = [f"movie{i}" for i in range(1, 15)]

# ------------------------------------------------------------------
# format results
# ------------------------------------------------------------------
for movie in movie_list:
    print(movie)

    in_file = os.path.join(r_path, f'ISRSA_personality_{movie}.csv')
    if not os.path.exists(in_file):
        print(f'File not found: {in_file}')
        continue

    tmp_df = pd.read_csv(in_file)

    # merge label information onto results
    merged_df = pd.merge(
        labels_df,
        tmp_df,
        left_on='one_based',
        right_on='Parcel'
    )

    # keep columns in desired order
    columns_order = [
        'Parcel',
        'label',
        'Yeo_7network',
        'estimate',
        'statistic',
        'pval',
        'pvalFDR',
        'pvalFWE'
    ]

    merged_df = merged_df[columns_order]

    # keep only FWE-significant parcels
    filtered_df = merged_df[merged_df['pvalFWE'] < 0.05]

    # save
    out_file = os.path.join(out_dir, f'ISRSA_personality_{movie}.csv')
    filtered_df.to_csv(out_file, index=False)