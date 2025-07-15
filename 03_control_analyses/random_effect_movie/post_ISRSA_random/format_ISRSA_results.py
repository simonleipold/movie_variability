#!/usr/bin/env python
import os
import pandas as pd

## location of main project directory on HPC
proj_path = '/project/3011157.03/Simon/proj_2022_CABB_movie/'
## location of R output files to visualize
r_path = os.path.join(proj_path, 'Scripts', 'MovVar_CommsBio_Revision01', 'control_ISRSA','r_output_movie_random')
## location where visualizations and niftis will be stored
out_dir = os.path.join(proj_path, 'Scripts', 'MovVar_CommsBio_Revision01', 'control_ISRSA','r_output_movie_random','formatted')
if not os.path.exists(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    print('Directory %s created' % out_dir)

## load Brainnetome labels
labels_csv = os.path.join(proj_path, 'MRI', 'Brainnetome_atlas', 'Brainnetome_labels_cortical.csv')
labels_df = pd.read_csv(labels_csv)
# Define the mapping dictionary
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

# Apply the mapping to the 'Yeo_7network' column
labels_df['Yeo_7network'] = labels_df['Yeo_7network'].replace(network_mapping)

tmp_df = pd.read_csv(os.path.join(r_path, 'ISRSA_random_movie_Features_Post' + '.csv'))
# Merging the values from the labels to match the node values from the results csv
# Create a new column in labels_df with the formatted parcel name
labels_df["Parcel"] = "parcel" + labels_df["one_based"].astype(str)

# Merge on the new Parcel column
merged_df = pd.merge(labels_df, tmp_df, on="Parcel")

# Specify the order of columns you want to retain
columns_order = ['Parcel', 'label', 'Yeo_7network', 
                'estimate', 'statistic', 'pval',
                'pvalFDR','pvalFWE']

# Reorder the DataFrame and drop any columns not listed
merged_df = merged_df[columns_order]
# Filter the DataFrame to only include significant results
filtered_df = merged_df[merged_df['pvalFWE'] < 0.05]
# Save the merged DataFrame to a new CSV file
filtered_df.to_csv(os.path.join(out_dir, 'ISRSA_random_movie_Features_Post' + '.csv'), index=False)
