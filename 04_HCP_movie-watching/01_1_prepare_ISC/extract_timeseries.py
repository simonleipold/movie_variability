#!/usr/bin/env python3
import os
import pandas as pd

from nltools.data import Brain_Data
from nltools.mask import expand_mask
from nilearn.image import index_img

# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
projpath = '/project/3011157.03/Simon/proj_2022_CABB_movie/MRI'
movpath = '/project/3011157.03/hcp7t'
timing_dir = os.path.join(projpath, 'TimingsHPC7TMovies')

subjlist = pd.read_csv(os.path.join(projpath, 'subjectlist_hcp7T.csv'), dtype=str)
# subjlist = pd.read_csv(os.path.join(projpath, 'subjectlist_hcp7T_part4.csv'), dtype=str)

mask_path = os.path.join(projpath, 'groupmask_movies_hcp7T.nii.gz')
brainnetome_path = os.path.join(projpath, 'Brainnetome_atlas', 'BN_Atlas_210_cortical_1p6mm_hcp7T.nii.gz')

# ------------------------------------------------------------------
# atlas
# ------------------------------------------------------------------
mask = Brain_Data(brainnetome_path, mask=mask_path)
mask_x = expand_mask(mask)

# ------------------------------------------------------------------
# output
# ------------------------------------------------------------------
dir_out = os.path.join(projpath, 'hcp7T_ROI_timeseries')
os.makedirs(dir_out, exist_ok=True)

# ------------------------------------------------------------------
# run mapping
# ------------------------------------------------------------------
runs = {
    "MOVIE1": "tfMRI_MOVIE1_7T_AP",
    "MOVIE2": "tfMRI_MOVIE2_7T_PA",
    "MOVIE3": "tfMRI_MOVIE3_7T_PA",
    "MOVIE4": "tfMRI_MOVIE4_7T_AP",
}

# ------------------------------------------------------------------
# loop
# ------------------------------------------------------------------
for subj in subjlist["PID"]:

    print(f"\nProcessing subject {subj}")

    for mov, run_dir in runs.items():

        bold_path = os.path.join(
            movpath, subj, "MNINonLinear", "Results", run_dir, f"{run_dir}.nii.gz"
        )

        if not os.path.exists(bold_path):
            print(f"Missing: {bold_path}")
            continue

        print(f"  Run {mov}")

        data = Brain_Data(bold_path, mask=mask_path)

        timing_file = os.path.join(timing_dir, f"hpc7T_{mov}_timing.csv")
        timing_df = pd.read_csv(timing_file)

        for _, row in timing_df.iterrows():

            movie = row["Movie"]
            movienr = row["MovieNr"]

            # TR = 1s → seconds == indices
            start_idx = int(row["Onset"])
            end_idx   = int(row["Offset"])

            clip_data = data[start_idx:end_idx]

            roi = clip_data.extract_roi(mask)

            out_file = os.path.join(
                dir_out,
                f"sub{subj}_movie{movienr}_Average_ROI.csv"
            )

            pd.DataFrame(roi.T).to_csv(out_file, index=False)

print("\nDone.")
