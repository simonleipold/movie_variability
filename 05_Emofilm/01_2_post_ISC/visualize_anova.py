#!/usr/bin/env python3
## this script visualizes the results of the anova movie comparison of the ISC values
## it reads in the results of the anova and visualizes the results on a glass brain
## it also writes the results to nifti files (if needed)

## import libraries
import os
import pandas as pd
import matplotlib.pyplot as plt

from nltools.data import Brain_Data
from nltools.mask import expand_mask, roi_to_brain
from nltools.stats import threshold

from nilearn import plotting as nplot

## location of main project directory on HPC
proj_path = '/project/3011157.03/Simon/proj_2022_CABB_movie/'

## location of R output files to visualize
in_path = os.path.join(
    proj_path,
    'Scripts',
    'MovVar_ImagNeuro_Revision01',
    'Emofilm',
    'r_output_anova'
)

## location where visualizations and niftis will be stored
out_dir = os.path.join(
    proj_path,
    'Scripts',
    'MovVar_ImagNeuro_Revision01',
    'Emofilm',
    'visualizations'
)
if not os.path.exists(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    print('Directory %s created' % out_dir)

## location of group mask
mask_path = os.path.join(proj_path, 'MRI', 'groupmask_movies_emofilm.nii.gz')

## get brain parcellation (k = 210; Brainnetome)
mask_name = 'Brainnetome'
brainnetome_path = os.path.join(
    proj_path,
    'MRI',
    'Brainnetome_atlas',
    'BN_Atlas_210_cortical_2mm.nii.gz'
)
mask = Brain_Data(brainnetome_path, mask=mask_path)
mask_x = expand_mask(mask)

## location of F and p values
pvalues_csv = os.path.join(in_path, 'isc_anova.csv')

# Load results data
pvalues_df = pd.read_csv(pvalues_csv)

## visualize F-vals and thresholded p-values within glass brain and write niftis
beta_brain = roi_to_brain(pd.Series(pvalues_df.loc[:, 'Fval']), mask_x)
pval_brain = roi_to_brain(pd.Series(pvalues_df.loc[:, 'pfwe']), mask_x)

## plot and write unthresholded image
# nplot.plot_glass_brain(
#     beta_brain.to_nifti(),
#     colorbar=True,
#     plot_abs=False,
#     cmap="plasma"
# )
# plt.savefig(
#     os.path.join(out_dir, 'ANOVA_ISC_movie_comparison_unthresholded.png'),
#     dpi=400
# )
# plt.close()
# beta_brain.to_nifti().to_filename(
#     os.path.join(out_dir, 'ANOVA_ISC_movie_comparison_unthresholded.nii.gz')
# )

## plot and write thresholded image
nplot.plot_glass_brain(
    threshold(beta_brain, pval_brain, thr=0.05).to_nifti(),
    colorbar=True,
    plot_abs=False,
    cmap="plasma",
    vmin=0,
    vmax=15,
    threshold=1e-12
)

plt.savefig(
    os.path.join(out_dir, 'ANOVA_ISC_movie_comparison.png'),
    dpi=400
)
plt.close()

# threshold(beta_brain, pval_brain, thr=0.05).to_nifti().to_filename(
#     os.path.join(out_dir, 'ANOVA_ISC_movie_comparison.nii.gz')
# )
