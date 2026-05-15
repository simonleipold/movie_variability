#!/usr/bin/env python3
import os
import pandas as pd
from nilearn import masking as nmask

# ------------------------------------------------------------------
# Create group mask across subjects for HCP 7T movie data
# ------------------------------------------------------------------

# base directory of HCP 7T data
base_path = "/project/3011157.03/hcp7t"

# subject list
subjlist_path = "/project/3011157.03/Simon/proj_2022_CABB_movie/MRI/subjectlist_hcp7T.csv"

# output directory for group mask
dir_out = "/project/3011157.03/Simon/proj_2022_CABB_movie/MRI"

# output filename
out_file = os.path.join(dir_out, "groupmask_movies_hcp7T.nii.gz")

# movie run folders per subject
run_dirs = [
    "tfMRI_MOVIE1_7T_AP",
    "tfMRI_MOVIE2_7T_PA",
    "tfMRI_MOVIE3_7T_PA",
    "tfMRI_MOVIE4_7T_AP",
]

# mask filename within each run folder
mask_name = "brainmask_fs.1.60.nii.gz"

# ------------------------------------------------------------------
# Load subject list
# ------------------------------------------------------------------
subjlist = pd.read_csv(subjlist_path)

# ------------------------------------------------------------------
# Collect mask files
# ------------------------------------------------------------------
mask_list = []

for subj in subjlist["PID"].astype(str):
    for run in run_dirs:
        mask_file = os.path.join(
            base_path,
            subj,
            "MNINonLinear",
            "Results",
            run,
            mask_name
        )

        if os.path.exists(mask_file):
            mask_list.append(mask_file)
        else:
            print(f"Missing mask: {mask_file}")

# ------------------------------------------------------------------
# Create group mask
# ------------------------------------------------------------------
print(f"Found {len(mask_list)} masks.")
groupmask = nmask.intersect_masks(mask_list, threshold=0.8)
groupmask.to_filename(out_file)

print(f"Saved group mask to: {out_file}")