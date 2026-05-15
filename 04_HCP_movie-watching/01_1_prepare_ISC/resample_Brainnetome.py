#!/usr/bin/env python3
import os
import matplotlib.pyplot as plt
from nilearn.image import load_img, resample_to_img
from nilearn import plotting as nplot

# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
projpath = "/project/3011157.03/Simon/proj_2022_CABB_movie/MRI"

atlas_in = os.path.join(
    projpath,
    "Brainnetome_atlas",
    "BN_Atlas_210_cortical_2mm.nii.gz"
)

target_mask = os.path.join(
    projpath,
    "groupmask_movies_hcp7T.nii.gz"
)

atlas_out = os.path.join(
    projpath,
    "Brainnetome_atlas",
    "BN_Atlas_210_cortical_1p6mm_hcp7T.nii.gz"
)

plot_out = os.path.join(
    projpath,
    "Brainnetome_atlas",
    "BN_Atlas_210_cortical_1p6mm_hcp7T_check.png"
)

# ------------------------------------------------------------------
# load images
# ------------------------------------------------------------------
atlas_img = load_img(atlas_in)
mask_img = load_img(target_mask)

# ------------------------------------------------------------------
# resample atlas to mask space
# ------------------------------------------------------------------
atlas_resampled = resample_to_img(
    atlas_img,
    mask_img,
    interpolation="nearest",
    force_resample=True,
    copy_header=True
)

# ------------------------------------------------------------------
# save resampled atlas
# ------------------------------------------------------------------
atlas_resampled.to_filename(atlas_out)

# ------------------------------------------------------------------
# sanity check plot (overlay atlas on mask)
# ------------------------------------------------------------------
display = nplot.plot_roi(
    atlas_resampled,
    bg_img=mask_img,
    title="Brainnetome atlas (resampled to 1.6mm)",
    display_mode="ortho",
    cut_coords=(0, 0, 0)
)

plt.savefig(plot_out, dpi=300, bbox_inches="tight")
plt.close()
