#!/usr/bin/env python
"""
Visualize parcel-wise ANOVA results for between-movie ISC differences
using the Schaefer 2018 300-parcel, 17-network atlas.
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

in_path = os.path.join(main_out_dir, "r_output_anova")
out_dir = os.path.join(main_out_dir, "visualizations")
nifti_dir = os.path.join(main_out_dir, "niftis")

for this_dir in [out_dir, nifti_dir]:
    if not os.path.exists(this_dir):
        os.makedirs(this_dir, exist_ok=True)
        print("Directory %s created" % this_dir)

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
# load ANOVA results
# ------------------------------------------------------------------
pvalues_csv = os.path.join(in_path, "isc_anova.csv")
pvalues_df = pd.read_csv(pvalues_csv)

# Ensure correct parcel order before mapping values back to brain space.
pvalues_df = pvalues_df.sort_values("Parcel").reset_index(drop=True)

if len(pvalues_df) != 300:
    print("WARNING: Expected 300 parcels, found %s." % len(pvalues_df))


# ------------------------------------------------------------------
# create brain images
# ------------------------------------------------------------------
f_brain = roi_to_brain(pd.Series(pvalues_df["Fval"].values), mask_x)
p_brain = roi_to_brain(pd.Series(pvalues_df["pfwe"].values), mask_x)

f_brain_thresholded = threshold(f_brain, p_brain, thr=0.05)


# ------------------------------------------------------------------
# save NIfTI files
# ------------------------------------------------------------------
# f_brain.to_nifti().to_filename(
#     os.path.join(nifti_dir, "ANOVA_ISC_movie_comparison_F_unthresholded.nii.gz")
# )

# f_brain_thresholded.to_nifti().to_filename(
#     os.path.join(nifti_dir, "ANOVA_ISC_movie_comparison_F_FWE005.nii.gz")
# )


# ------------------------------------------------------------------
# plot thresholded F-map
# ------------------------------------------------------------------
nplot.plot_glass_brain(
    f_brain_thresholded.to_nifti(),
    colorbar=True,
    plot_abs=False,
    cmap="plasma",
    vmin=0,
    vmax=20,
    threshold=1e-12,
    # title="Between-movie ISC variability, FWE p < .05",
)

plt.savefig(
    os.path.join(out_dir, "ANOVA_ISC_movie_comparison.png"),
    dpi=400,
)
plt.close()

print("Saved thresholded ANOVA visualization.")
# print("Saved ANOVA NIfTI files.")