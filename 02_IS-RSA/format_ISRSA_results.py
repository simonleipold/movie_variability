#!/usr/bin/env python
import os
import pandas as pd

## location of main project directory on HPC
proj_path = '/project/3011157.03/Simon/proj_2022_CABB_movie/'
## location of R output files to visualize
r_path = os.path.join(proj_path, 'Scripts', '04_2ndLev_ISRSA','r_output')
## location where visualizations and niftis will be stored
out_dir = os.path.join(proj_path, 'Scripts', '04_2ndLev_ISRSA','r_output','formatted')
if not os.path.exists(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    print('Directory %s created' % out_dir)

## create a task list for plots and files
task_flist = ['ISRSA_features_post_', 'ISRSA_features_pre_', 'ISRSA_naming_post_', 'ISRSA_naming_pre_']
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

## format the results
for i, f in enumerate(task_flist):
    for j, m in enumerate(["movie1", "movie2", "movie3", "movie4", "movie5", "movie6", "movie7", "movie8"]):
        print(f)
        print(m)
        tmp_df = pd.read_csv(os.path.join(r_path, f + m + '.csv'))
        # Merging the values from the labels to match the node values from the results csv
        merged_df = pd.merge(labels_df, tmp_df, left_on='one_based', right_on='Parcel')

        # Specify the order of columns you want to retain
        columns_order = ['Parcel', 'label', 'Yeo_7network', 
                        'estimate', 'statistic', 'pval',
                        'pvalFDR','pvalFWE']

        # Reorder the DataFrame and drop any columns not listed
        merged_df = merged_df[columns_order]
        # Filter the DataFrame to only include significant results
        filtered_df = merged_df[merged_df['pvalFWE'] < 0.05]
        # Save the merged DataFrame to a new CSV file
        filtered_df.to_csv(os.path.join(out_dir, f + m + '.csv'), index=False)