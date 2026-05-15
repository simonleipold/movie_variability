#!/usr/bin/env python
"""
Visualize Schaefer IS-RSA results on glass brains.

This script reads the IS-RSA R output files and visualizes thresholded
t-statistic maps for the Features_Post effect for each movie.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

from nltools.data import Brain_Data
from nltools.mask import expand_mask, roi_to_brain
from nltools.stats import threshold

from nilearn import plotting as nplot


# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
proj_path = "/project/3011157.03/Simon/proj_2022_CABB_movie"

main_out_dir = os.path.join(
    proj_path,
    "Scripts",
    "MovVar_ImagNeuro_Revision01",
    "CABB_Schaefer",
)

r_path = os.path.join(main_out_dir, "r_output_isrsa")
out_dir = os.path.join(main_out_dir, "visualizations")

if not os.path.exists(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    print("Directory %s created" % out_dir)

mask_path = os.path.join(proj_path, "MRI", "groupmask_movies.nii.gz")


# ------------------------------------------------------------------
# atlas settings: Schaefer 2018, 300 parcels, 17 networks
# ------------------------------------------------------------------
mask_name = "Schaefer2018_300Parcels_17Networks"

schaefer_path = os.path.join(
    proj_path,
    "MRI",
    "Schaefer_atlas",
    "Schaefer2018_300Parcels_17Networks_order_FSLMNI152_2mm_space-BNAtlas.nii.gz",
)

mask = Brain_Data(schaefer_path, mask=mask_path)
mask_x = expand_mask(mask)


# ------------------------------------------------------------------
# files to visualize
# ------------------------------------------------------------------
task_flist = ["ISRSA_features_post_"]

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


# ------------------------------------------------------------------
# visualize thresholded t-statistic maps
# ------------------------------------------------------------------
for task in task_flist:
    for movie in movie_list:
        
        print(task)
        print(movie)
        
        csv_file = os.path.join(r_path, task + movie + ".csv")
        
        if not os.path.exists(csv_file):
            print("File not found: %s" % csv_file)
            continue
        
        tmp_df = pd.read_csv(csv_file)
        
        # Ensure correct Schaefer parcel order before mapping to brain.
        tmp_df = tmp_df.sort_values("Parcel").reset_index(drop=True)
        
        if len(tmp_df) != 300:
            print("WARNING: Expected 300 parcels, found %s in %s" % (len(tmp_df), csv_file))
        
        beta_brain = roi_to_brain(pd.Series(tmp_df["statistic"].values), mask_x)
        pval_fwe_brain = roi_to_brain(pd.Series(tmp_df["pvalFWE"].values), mask_x)
        
        thresholded_brain = threshold(
            beta_brain,
            pval_fwe_brain,
            thr=0.05,
        )
        
        display = nplot.plot_glass_brain(
            thresholded_brain.to_nifti(),
            colorbar=True,
            plot_abs=False,
            vmin=-6.00,
            vmax=6.00,
            cmap="inferno",
            threshold=1e-12,
        )
        
        plt.savefig(
            os.path.join(out_dir, "%s%s_pFWE005.png" % (task, movie)),
            dpi=400,
            # bbox_inches="tight",
        )
        plt.close()

print("\nFinished visualizing Schaefer IS-RSA results.")