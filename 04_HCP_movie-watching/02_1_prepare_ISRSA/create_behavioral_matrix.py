#!/usr/bin/env python3
## create personality distance matrix (correlation distance across 5 traits)

import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import pairwise_distances

# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
projpath = '/project/3011157.03/Simon/proj_2022_CABB_movie'

data_path = os.path.join(
    projpath,
    'MRI',
    'subjectlist_hcp7T_personality.csv'
)

dir_out = os.path.join(
    projpath,
    'Scripts',
    'MovVar_ImagNeuro_Revision01',
    'HCP_movie-watching',
    'matrices_behavior'
)

dir_out_vis = os.path.join(dir_out, 'visualizations')

os.makedirs(dir_out, exist_ok=True)
os.makedirs(dir_out_vis, exist_ok=True)

# ------------------------------------------------------------------
# load data
# ------------------------------------------------------------------
df = pd.read_csv(data_path, dtype=str)

# convert personality scores to numeric
traits = ['NEOFAC_A', 'NEOFAC_O', 'NEOFAC_C', 'NEOFAC_N', 'NEOFAC_E']
df[traits] = df[traits].apply(pd.to_numeric)

# ------------------------------------------------------------------
# compute correlation distance matrix
# ------------------------------------------------------------------
data = df[traits].values

distance_matrix = pairwise_distances(
    data,
    metric='correlation'
)

# ------------------------------------------------------------------
# store as dataframe
# ------------------------------------------------------------------
pids = df['PID'].astype(str)

distance_df = pd.DataFrame(
    distance_matrix,
    index=pids,
    columns=pids
)

# save
out_file = os.path.join(dir_out, 'personality_distance_matrix.csv')
distance_df.to_csv(out_file)

print(f'Saved: {out_file}')

# ------------------------------------------------------------------
# visualization
# ------------------------------------------------------------------
sns.set_theme(style="white")

plt.figure(figsize=(10, 8))
sns.heatmap(distance_df.astype(float), cmap="viridis", square=True)

plt.xlabel("Participant")
plt.ylabel("Participant")

plt.savefig(
    os.path.join(dir_out_vis, 'personality_distance_matrix.png'),
    dpi=400
)

plt.close()