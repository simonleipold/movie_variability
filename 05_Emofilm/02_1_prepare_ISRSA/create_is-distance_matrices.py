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
    os.path.join(projpath, 'MRI', 'subjectlist_emofilm_personality.csv'),
    dtype=str
)

mov_csv_path = os.path.join(
    projpath,
    'MRI',
    'Emofilm_ROI_timeseries'
)

# ------------------------------------------------------------------
# output
# ------------------------------------------------------------------
dir_out = os.path.join(
    projpath,
    'Scripts',
    'MovVar_ImagNeuro_Revision01',
    'Emofilm',
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
    subjects_used = []

    for subj in subjlist['PID']:
        sub_file = os.path.join(
            mov_csv_path,
            f'{subj}_movie{movie}_Average_ROI.csv'
        )

        if not os.path.exists(sub_file):
            raise FileNotFoundError(f'Missing ROI timeseries file: {sub_file}')

        sub_data = pd.read_csv(sub_file)
        sub_timeseries.append(sub_data.values)
        subjects_used.append(subj)

    # determine maximum number of time points for this movie
    max_n_ts = max(ts.shape[0] for ts in sub_timeseries)

    # zero-pad shorter time series
    sub_timeseries_padded = []

    for subj, ts in zip(subjects_used, sub_timeseries):
        n_ts, n_parcels = ts.shape

        if n_ts < max_n_ts:
            n_missing = max_n_ts - n_ts
            print(f"Padding {subj}: {n_ts} -> {max_n_ts} time points")

            pad_rows = np.zeros((n_missing, n_parcels))
            ts = np.vstack([ts, pad_rows])

        sub_timeseries_padded.append(ts)

    data = np.array(sub_timeseries_padded)
    n_subs, n_ts, n_parcels = data.shape
    # print(data.shape)

    for parcel in range(n_parcels):

        distance_matrix = pairwise_distances(
            data[:, :, parcel],
            metric='correlation'
        )

        df = pd.DataFrame(
            distance_matrix,
            index=subjects_used,
            columns=subjects_used
        )

        df.to_csv(
            os.path.join(dir_out, f'movie{movie}_parcel{parcel+1}.csv'),
            index=True,
            header=True
        )