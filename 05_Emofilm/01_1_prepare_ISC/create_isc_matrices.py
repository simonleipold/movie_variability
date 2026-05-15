#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from nltools.data import Brain_Data, Adjacency
from nltools.mask import expand_mask, roi_to_brain
from nilearn import plotting as nplot
from sklearn.metrics import pairwise_distances

# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
projpath = '/project/3011157.03/Simon/proj_2022_CABB_movie'

subjlist = pd.read_csv(
    os.path.join(projpath, 'MRI', 'subjectlist_emofilm_personality.csv'),
    dtype=str
)

mask_path = os.path.join(
    projpath,
    'MRI',
    'groupmask_movies_emofilm.nii.gz'
)

brainnetome_path = os.path.join(
    projpath,
    'MRI',
    'Brainnetome_atlas',
    'BN_Atlas_210_cortical_2mm.nii.gz'
)

mov_csv_path = os.path.join(
    projpath,
    'MRI',
    'Emofilm_ROI_timeseries'
)

# ------------------------------------------------------------------
# output
# ------------------------------------------------------------------
base_out = os.path.join(
    projpath,
    'Scripts',
    'MovVar_ImagNeuro_Revision01',
    'Emofilm'
)

dir_out = os.path.join(base_out, 'matrices')
dir_out_vis = os.path.join(base_out, 'visualizations')

os.makedirs(dir_out, exist_ok=True)
os.makedirs(dir_out_vis, exist_ok=True)

# ------------------------------------------------------------------
# atlas
# ------------------------------------------------------------------
mask = Brain_Data(brainnetome_path, mask=mask_path)
mask_x = expand_mask(mask)

# ------------------------------------------------------------------
# movies 1–14
# ------------------------------------------------------------------
movie_list = range(1, 15)

# ------------------------------------------------------------------
# ISC computation
# ------------------------------------------------------------------
for movie_nr in movie_list:

    print(f'Processing movie {movie_nr}')

    sub_timeseries = []
    subjects_used = []

    for subj in subjlist['PID']:

        sub_file = os.path.join(
            mov_csv_path,
            f"{subj}_movie{movie_nr}_Average_ROI.csv"
        )

        if not os.path.exists(sub_file):
            raise FileNotFoundError(f'Missing ROI timeseries file: {sub_file}')

        sub_data = pd.read_csv(sub_file)
        sub_timeseries.append(sub_data.values)
        subjects_used.append(subj)
    # zero-pad shorter time series
    max_n_ts = max(ts.shape[0] for ts in sub_timeseries)

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

    similarity_matrices = []

    for parcel in range(n_parcels):

        similarity_matrix = 1 - pairwise_distances(
            data[:, :, parcel],
            metric='correlation'
        )

        similarity_matrices.append(
            Adjacency(similarity_matrix, matrix_type='similarity')
        )

        df = pd.DataFrame(
            similarity_matrix,
            index=subjects_used,
            columns=subjects_used
        )

        df.to_csv(
            os.path.join(
                dir_out,
                f'ISC_movie{movie_nr}_parcel{parcel+1}.csv'
            )
        )

    # --------------------------------------------------------------
    # mean ISC visualization
    # --------------------------------------------------------------
    isc = {
        parcel: similarity_matrices[parcel].isc(
            metric='mean',
            n_samples=1,
            n_jobs=1
        )['isc']
        for parcel in range(n_parcels)
    }

    isc_brain = roi_to_brain(pd.Series(isc), expand_mask(mask))

    nplot.plot_glass_brain(
        isc_brain.to_nifti(),
        colorbar=True,
        plot_abs=False,
        cmap="viridis",
        vmin=-0.5,
        vmax=0.5,
        threshold=1e-12
    )

    plt.savefig(
        os.path.join(
            dir_out_vis,
            f'Mean_ISC_movie{movie_nr}.png'
        ),
        dpi=400
    )

    plt.close()