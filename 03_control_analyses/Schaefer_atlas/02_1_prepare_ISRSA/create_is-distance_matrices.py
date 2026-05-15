#!/usr/bin/env python
"""
Create correlation-distance matrices for IS-RSA.

For each movie and Schaefer parcel, this script computes the pairwise
correlation distance between subjects' parcel-wise fMRI time series.

Correlation distance = 1 - Pearson correlation.
"""

import os
import pandas as pd
import numpy as np

from sklearn.metrics import pairwise_distances


# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
projpath = "/project/3011157.03/Simon/proj_2022_CABB_movie"
print("The main project directory is located here: %s" % projpath)

fmriprep_dir = os.path.join(projpath, "MRI", "BIDS_movie")

subjlist = pd.read_csv(
    os.path.join(projpath, "MRI", "subjectlist.csv"),
    dtype=object,
)


# ------------------------------------------------------------------
# atlas settings: Schaefer 2018, 300 parcels, 17 networks
# ------------------------------------------------------------------
mask_name = "Schaefer2018_300Parcels_17Networks"
n_parcels_expected = 300


# ------------------------------------------------------------------
# input: extracted Schaefer ROI time series
# ------------------------------------------------------------------
mov_csv_path = os.path.join(
    fmriprep_dir,
    "derivatives",
    "secLev_nltools_ISC_ROI",
    mask_name,
    "csv_files",
)


# ------------------------------------------------------------------
# output directory
# ------------------------------------------------------------------
main_out_dir = os.path.join(
    projpath,
    "Scripts",
    "MovVar_ImagNeuro_Revision01",
    "CABB_Schaefer",
)

dir_out = os.path.join(main_out_dir, "matrices_distance")

if not os.path.exists(dir_out):
    os.makedirs(dir_out, exist_ok=True)
    print("Dir %s created" % dir_out)


# ------------------------------------------------------------------
# create correlation-distance matrices for each movie and parcel
# ------------------------------------------------------------------
movie_list = [
    "movie1",
    "movie2",
    "movie3",
    "movie4",
    "movie5",
    "movie6",
    "movie7",
    "movie8",
]

for movie in movie_list:
    print("\nProcessing %s" % movie)

    # --------------------------------------------------------------
    # load extracted time series for all subjects
    # --------------------------------------------------------------
    sub_timeseries = []

    for subj in subjlist["PID"]:
        csv_file = os.path.join(
            mov_csv_path,
            "sub%s_%s_Average_ROI.csv" % (subj, movie),
        )

        if not os.path.exists(csv_file):
            raise FileNotFoundError("Missing ROI CSV file: %s" % csv_file)

        sub_data = pd.read_csv(csv_file)
        sub_timeseries.append(sub_data.values)

    data = np.array(sub_timeseries)
    n_subs, n_ts, n_parcels = data.shape

    print(
        "Loaded data with shape: subjects=%s, timepoints=%s, parcels=%s"
        % (n_subs, n_ts, n_parcels)
    )

    if n_parcels != n_parcels_expected:
        print(
            "WARNING: Expected %s parcels, but loaded %s parcels."
            % (n_parcels_expected, n_parcels)
        )

    # --------------------------------------------------------------
    # calculate correlation-distance matrix for each parcel
    # --------------------------------------------------------------
    for parcel in range(n_parcels):
        distance_matrix = pairwise_distances(
            data[:, :, parcel],
            metric="correlation",
        )

        df = pd.DataFrame(
            distance_matrix,
            index=subjlist["PID"],
            columns=subjlist["PID"],
        )

        df.to_csv(
            os.path.join(
                dir_out,
                "%s_parcel%s.csv" % (movie, parcel + 1),
            ),
            index=True,
            header=True,
        )

print("\nFinished creating IS-RSA correlation-distance matrices.")