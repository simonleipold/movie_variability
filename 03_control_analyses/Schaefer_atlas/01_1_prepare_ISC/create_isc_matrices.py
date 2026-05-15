#!/usr/bin/env python
import os
import warnings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from nltools.data import Brain_Data
from nltools.mask import expand_mask, roi_to_brain

from nilearn import plotting as nplot
from sklearn.metrics import pairwise_distances

warnings.filterwarnings("ignore")


# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
projpath = "/project/3011157.03/Simon/proj_2022_CABB_movie/"
print("The main project directory is located here: %s" % projpath)

fmriprep_dir = os.path.join(projpath, "MRI", "BIDS_movie")

subjlist = pd.read_csv(
    os.path.join(projpath, "MRI", "subjectlist.csv"),
    dtype=object,
)

mask_path = os.path.join(projpath, "MRI", "groupmask_movies.nii.gz")


# ------------------------------------------------------------------
# atlas settings: Schaefer 2018, 300 parcels, 17 networks
# ------------------------------------------------------------------
mask_name = "Schaefer2018_300Parcels_17Networks"
n_parcels_expected = 300

schaefer_dir = os.path.join(projpath, "MRI", "Schaefer_atlas")

schaefer_path = os.path.join(
    schaefer_dir,
    "Schaefer2018_300Parcels_17Networks_order_FSLMNI152_2mm_space-BNAtlas.nii.gz",
)

labels_path = os.path.join(
    schaefer_dir,
    "Schaefer2018_300Parcels_17Networks_order_FSLMNI152_2mm_labels.tsv",
)

mask = Brain_Data(schaefer_path, mask=mask_path)
mask_x = expand_mask(mask)

atlas_labels = pd.read_csv(labels_path, sep="\t")

if len(atlas_labels) != n_parcels_expected:
    print(
        "WARNING: Expected %s labels, but found %s."
        % (n_parcels_expected, len(atlas_labels))
    )


# ------------------------------------------------------------------
# location of extracted Schaefer movie fMRI time series
# ------------------------------------------------------------------
mov_csv_path = os.path.join(
    fmriprep_dir,
    "derivatives",
    "secLev_nltools_ISC_ROI",
    mask_name,
    "csv_files",
)


# ------------------------------------------------------------------
# main output directory
# ------------------------------------------------------------------
main_out_dir = (
    "/project/3011157.03/Simon/proj_2022_CABB_movie/"
    "Scripts/MovVar_ImagNeuro_Revision01/CABB_Schaefer"
)

dir_out_matrices = os.path.join(main_out_dir, "matrices")
dir_out_vis = os.path.join(main_out_dir, "visualizations")
dir_out_isc = os.path.join(main_out_dir, "isc_values")

for this_dir in [main_out_dir, dir_out_matrices, dir_out_vis, dir_out_isc]:
    if not os.path.exists(this_dir):
        os.makedirs(this_dir)
        print("Dir %s created" % this_dir)


# ------------------------------------------------------------------
# create ISC matrices for each movie
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

all_isc_values = []

for movie in movie_list:
    print("\nProcessing %s" % movie)

    # --------------------------------------------------------------
    # load extracted time series
    # --------------------------------------------------------------
    sub_timeseries = []

    for subj in subjlist["PID"]:
        csv_path = os.path.join(
            mov_csv_path,
            "sub%s_%s_Average_ROI.csv" % (subj, movie),
        )

        if not os.path.exists(csv_path):
            raise FileNotFoundError("Missing ROI CSV file: %s" % csv_path)

        sub_data = pd.read_csv(csv_path)
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
    # calculate ISC matrix and mean ISC for each parcel
    # --------------------------------------------------------------
    isc_values = {}

    upper_tri = np.triu_indices(n_subs, k=1)

    for parcel in range(n_parcels):
        similarity_matrix = 1 - pairwise_distances(
            data[:, :, parcel],
            metric="correlation",
        )

        df_matrix = pd.DataFrame(
            similarity_matrix,
            index=subjlist["PID"],
            columns=subjlist["PID"],
        )

        df_matrix.to_csv(
            os.path.join(
                dir_out_matrices,
                "ISC_%s_parcel%s.csv" % (movie, parcel + 1),
            ),
            index=True,
            header=True,
        )

        isc_values[parcel] = np.nanmean(similarity_matrix[upper_tri])

    # --------------------------------------------------------------
    # save mean ISC values
    # --------------------------------------------------------------
    df_isc = pd.DataFrame({
        "zero_based": np.arange(n_parcels),
        "parcel": np.arange(1, n_parcels + 1),
        "movie": movie,
        "ISC": pd.Series(isc_values),
    })

    df_isc = df_isc.merge(
        atlas_labels[["zero_based", "label", "Yeo_17_network"]],
        on="zero_based",
        how="left",
    )

    df_isc = df_isc[
        [
            "zero_based",
            "parcel",
            "label",
            "Yeo_17_network",
            "movie",
            "ISC",
        ]
    ]

    df_isc.to_csv(
        os.path.join(dir_out_isc, "ISC_%s.csv" % movie),
        index=False,
    )

    all_isc_values.append(df_isc)

    # --------------------------------------------------------------
    # visualize mean ISC per parcel
    # --------------------------------------------------------------
    isc_brain = roi_to_brain(pd.Series(isc_values), mask_x)

    nplot.plot_glass_brain(
        isc_brain.to_nifti(),
        colorbar=True,
        plot_abs=False,
        cmap="viridis",
        vmin=-0.5,
        vmax=0.5,
        threshold=1e-12,
        # title="Mean ISC: %s, %s" % (movie, mask_name),
    )

    plt.savefig(
        os.path.join(dir_out_vis, "Mean_ISC_%s.png" % movie),
        dpi=400,
        bbox_inches="tight",
    )
    plt.close()


# ------------------------------------------------------------------
# save combined ISC dataframe
# ------------------------------------------------------------------
df_all_isc = pd.concat(all_isc_values, axis=0, ignore_index=True)

df_all_isc.to_csv(
    os.path.join(dir_out_isc, "ISC_all_movies.csv"),
    index=False,
)

print("\nFinished ISC matrix creation and mean ISC visualization.")