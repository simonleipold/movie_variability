#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np

from sklearn.metrics import pairwise_distances

# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
projpath = '/project/3011157.03/Simon/proj_2022_CABB_movie'

subjlist = pd.read_csv(
    os.path.join(projpath, 'MRI', 'subjectlist_hcp7T.csv'),
    dtype=str
)

mov_csv_path = os.path.join(
    projpath,
    'MRI',
    'hcp7T_ROI_timeseries'
)

# ------------------------------------------------------------------
# output
# ------------------------------------------------------------------
dir_out = os.path.join(
    projpath,
    'Scripts',
    'MovVar_ImagNeuro_Revision01',
    'HCP_movie-watching',
    'matrices_distance'
)

os.makedirs(dir_out, exist_ok=True)

# ------------------------------------------------------------------
# movies 1–14
# ------------------------------------------------------------------
movie_list = range(1, 15)

# ------------------------------------------------------------------
# compute correlation-distance matrices
# ------------------------------------------------------------------
for movie in movie_list:
    print(f'Processing movie {movie}')

    sub_timeseries = []

    for subj in subjlist['PID']:
        sub_file = os.path.join(
            mov_csv_path,
            f'sub{subj}_movie{movie}_Average_ROI.csv'
        )

        sub_data = pd.read_csv(sub_file)
        sub_timeseries.append(sub_data.values)

    data = np.array(sub_timeseries)
    n_subs, n_ts, n_parcels = data.shape

    for parcel in range(n_parcels):

        distance_matrix = pairwise_distances(
            data[:, :, parcel],
            metric='correlation'
        )

        df = pd.DataFrame(
            distance_matrix,
            index=subjlist['PID'],
            columns=subjlist['PID']
        )

        df.to_csv(
            os.path.join(dir_out, f'movie{movie}_parcel{parcel+1}.csv'),
            index=True,
            header=True
        )