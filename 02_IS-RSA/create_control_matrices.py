#!/usr/bin/env python
## this script first generates a participant by participant matrix
## to incorporate distance in age and sex between the participants
## (absolute distance in age, and 0 if same sex, 1 if different sex)

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns

# location of main project directory on HPC
projpath = '/project/3011157.03/Simon/proj_2022_CABB_movie/MRI'

## where should new matrices be stored?
dir_out = os.path.join('/project', '3011157.03', 'Simon', 'proj_2022_CABB_movie', 'Scripts', '04_2ndLev_ISRSA', 'matrices')
if not os.path.exists(dir_out):
    os.makedirs(dir_out, exist_ok = True)
    print('directory %s created' % (dir_out))

## where should the matrix visualizations be stored?
dir_out_vis = os.path.join('/project', '3011157.03', 'Simon', 'proj_2022_CABB_movie', 'Scripts', '04_2ndLev_ISRSA', 'matrices', 'visualizations')
if not os.path.exists(dir_out_vis):
    os.makedirs(dir_out_vis, exist_ok = True)
    print('directory %s created' % (dir_out_vis))

## load the subjectlist with age and sex information
subjdata = pd.read_csv(os.path.join(projpath, 'subjectlist_age_sex.csv'), dtype = object)
subjdata['age'] = pd.to_numeric(subjdata['age'])

# Creating the Age Difference Matrix
# We'll use a nested loop approach to calculate the absolute age difference between each pair of subjects

# Extracting unique PIDs and initializing an empty DataFrame for age differences
unique_pids = subjdata['PID'].unique()
age_difference_df = pd.DataFrame(index=subjdata['PID'], columns=subjdata['PID'])

# Filling the DataFrame with age differences
for pid1 in unique_pids:
    for pid2 in unique_pids:
        age1 = subjdata[subjdata['PID'] == pid1]['age'].values[0]
        age2 = subjdata[subjdata['PID'] == pid2]['age'].values[0]
        age_difference_df.at[pid1, pid2] = abs(age1 - age2)

# save the age difference matrix as a CSV file
age_difference_df.to_csv(os.path.join(dir_out, 'Control_age.csv'), index = True, header = True)

# Creating the Sex Difference Matrix
# We'll use a similar approach for the sex difference
sex_difference_df = pd.DataFrame(index=subjdata['PID'], columns=subjdata['PID'])

# Filling the DataFrame with sex differences (0 if same, 1 if different)
for pid1 in unique_pids:
    for pid2 in unique_pids:
        sex1 = subjdata[subjdata['PID'] == pid1]['sex_char'].values[0]
        sex2 = subjdata[subjdata['PID'] == pid2]['sex_char'].values[0]
        sex_difference_df.at[pid1, pid2] = 0 if sex1 == sex2 else 1

sex_difference_df.to_csv(os.path.join(dir_out, 'Control_sex.csv'), index = True, header = True)

## visualize matrices

# Setting the aesthetics for the plots
sns.set_theme(style="white")

# Convert the dataframes to numeric types for visualization
age_difference_df = age_difference_df.astype(int)
sex_difference_df = sex_difference_df.astype(int)

# Plotting the Age Difference Matrix
plt.figure(figsize=(10, 8))
sns.heatmap(age_difference_df, cmap="plasma", square=True)
plt.xlabel("Participant")
plt.ylabel("Participant")
plt.savefig(os.path.join(dir_out_vis, 'age_difference_matrix.png'), dpi = 400)

# Creating a custom colormap for binary data
binary_cmap = mcolors.ListedColormap(['#00017A', '#FED701'])

# Plotting the Sex Difference Matrix
plt.figure(figsize=(10, 8))
ax = sns.heatmap(sex_difference_df, cmap=binary_cmap, square=True, cbar_kws={'ticks': [0, 1]})
colorbar = ax.collections[0].colorbar
colorbar.set_ticks([0, 1])
colorbar.set_ticklabels(['Same', 'Different'])
plt.xlabel("Participant")
plt.ylabel("Participant")
plt.savefig(os.path.join(dir_out_vis, 'sex_difference_matrix.png'), dpi=400)