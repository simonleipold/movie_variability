#!/usr/bin/env python
import os
import warnings

import pandas as pd
import matplotlib.pyplot as plt

from nltools.data import Brain_Data
from nilearn import plotting as nplot

warnings.filterwarnings("ignore")  # suppress warnings


# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
projpath = "/project/3011157.03/Simon/proj_2022_CABB_movie/MRI"
print("The main project directory is located here: %s" % projpath)

# location of preprocessed BIDS data
fmriprep_dir = os.path.join(projpath, "BIDS_movie")

# location of preprocessed, denoised, and smoothed data
movpath = os.path.join(fmriprep_dir, "derivatives", "nilearn")

# location of subject list
subjlist = pd.read_csv(os.path.join(projpath, "subjectlist.csv"), dtype=object)

# location of group mask
mask_path = os.path.join(projpath, "groupmask_movies.nii.gz")


# ------------------------------------------------------------------
# atlas settings
# ------------------------------------------------------------------
mask_name = "Schaefer2018_300Parcels_17Networks"
n_parcels = 300

schaefer_dir = os.path.join(projpath, "Schaefer_atlas")

schaefer_path = os.path.join(
    schaefer_dir,
    "Schaefer2018_300Parcels_17Networks_order_FSLMNI152_2mm_space-BNAtlas.nii.gz",
)

labels_path = os.path.join(
    schaefer_dir,
    "Schaefer2018_300Parcels_17Networks_order_FSLMNI152_2mm_labels.tsv",
)

mask = Brain_Data(schaefer_path, mask=mask_path)
atlas_labels = pd.read_csv(labels_path, sep="\t")

if len(atlas_labels) != n_parcels:
    print(
        "WARNING: Expected %s atlas labels, but found %s."
        % (n_parcels, len(atlas_labels))
    )


# ------------------------------------------------------------------
# output directory
# ------------------------------------------------------------------
dir_out = os.path.join(
    fmriprep_dir,
    "derivatives",
    "secLev_nltools_ISC_ROI",
    mask_name,
)

if not os.path.exists(dir_out):
    os.makedirs(dir_out)
    print("Dir %s created" % dir_out)


# ------------------------------------------------------------------
# plot atlas
# ------------------------------------------------------------------
plot_atlas = True

if plot_atlas:
    nplot.plot_roi(
        mask.to_nifti(),
        title="%s Parcellation" % mask_name,
        display_mode="ortho",
        draw_cross=False,
    )
    plt.savefig(
        os.path.join(dir_out, "CorticalParcels_%s.png" % mask_name),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


# ------------------------------------------------------------------
# extract average time series from atlas and save to CSV
# ------------------------------------------------------------------
extract_csv = True

dir_out_csv = os.path.join(dir_out, "csv_files")

if extract_csv:
    if not os.path.exists(dir_out_csv):
        os.makedirs(dir_out_csv)
        print("Dir %s created" % dir_out_csv)

    for scan in [
        "movie1",
        "movie2",
        "movie3",
        "movie4",
        "movie5",
        "movie6",
        "movie7",
        "movie8",
    ]:
        for subj in subjlist["PID"]:
            print("Extracting ROI time series: subject %s, %s" % (subj, scan))

            img_path = os.path.join(
                movpath,
                "sub-%s" % subj,
                "s_%s_img.nii.gz" % scan,
            )

            if not os.path.exists(img_path):
                print("WARNING: File not found, skipping: %s" % img_path)
                continue

            data = Brain_Data(img_path, mask=mask_path)
            roi = data.extract_roi(mask)

            roi_df = pd.DataFrame(roi.T)

            if roi_df.shape[1] != n_parcels:
                print(
                    "WARNING: Expected %s parcels, but extracted %s parcels for subject %s, %s."
                    % (n_parcels, roi_df.shape[1], subj, scan)
                )

            roi_df.to_csv(
                os.path.join(
                    dir_out_csv,
                    "sub%s_%s_Average_ROI.csv" % (subj, scan),
                ),
                index=False,
            )

print("Finished extracting Schaefer ROI time series.")