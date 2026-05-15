#!/usr/bin/env python3
import os
import pandas as pd
from nilearn import masking as nmask
from nilearn import image as nimg

# ------------------------------------------------------------------
# Create group mask across subjects for Emofilm movie data
# using preprocessed BOLD files
# ------------------------------------------------------------------

# base directory of preprocessed Emofilm data
base_path = "/project/3011157.03/ds004892/derivatives/preprocessing"

# helper files
subjlist_path = "/project/3011157.03/Simon/proj_2022_CABB_movie/MRI/subjectlist_emofilm_personality.csv"
tasks_path = "/project/3011157.03/Simon/proj_2022_CABB_movie/MRI/tasks_emofilm.tsv"

# output directory
dir_out = "/project/3011157.03/Simon/proj_2022_CABB_movie/MRI"
mask_dir = os.path.join(dir_out, "masks_emofilm")
os.makedirs(mask_dir, exist_ok=True)

# output filename for final group mask
out_file = os.path.join(dir_out, "groupmask_movies_emofilm.nii.gz")

# threshold for intersecting masks
groupmask_threshold = 0.8

# ------------------------------------------------------------------
# Load input tables
# ------------------------------------------------------------------
subjlist = pd.read_csv(subjlist_path)
tasks_df = pd.read_csv(tasks_path, sep="\t")

# ------------------------------------------------------------------
# Compute run-wise masks from BOLD files
# ------------------------------------------------------------------
mask_list = []
missing_files = []

for _, row in tasks_df.iterrows():
    subj = row["subject"]
    ses = row["session"]
    task = row["task"]

    bold_file = os.path.join(
        base_path,
        subj,
        ses,
        "func",
        f"{subj}_{ses}_task-{task}_space-MNI_desc-ppres_bold.nii.gz"
    )

    mask_file = os.path.join(
        mask_dir,
        f"{subj}_{ses}_task-{task}_mask.nii.gz"
    )

    if os.path.exists(bold_file):
        print(f"Computing mask for: {bold_file}")
        # Mean across time
        mean_bold = nimg.mean_img(bold_file)

        # Mask = all voxels whose mean signal is not zero
        run_mask = nimg.math_img("img != 0", img=mean_bold)
        run_mask.to_filename(mask_file)
        mask_list.append(mask_file)
    else:
        print(f"Missing BOLD file: {bold_file}")
        missing_files.append(bold_file)

# ------------------------------------------------------------------
# Create group mask
# ------------------------------------------------------------------
if len(mask_list) == 0:
    raise RuntimeError("No masks were created. Check paths and filenames.")

print(f"Created {len(mask_list)} run-wise masks.")
print(f"Missing {len(missing_files)} BOLD files.")

groupmask = nmask.intersect_masks(mask_list, threshold=groupmask_threshold)
groupmask.to_filename(out_file)

print(f"Saved group mask to: {out_file}")