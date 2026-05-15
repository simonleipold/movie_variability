#!/usr/bin/env python
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
r_path = os.path.join(proj_path, 'Scripts', 'MovVar_CommsBio_Revision01', 'control_ISRSA','r_output_movie_random')
## location where visualizations and niftis will be stored
out_dir = os.path.join(proj_path, 'Scripts', 'MovVar_CommsBio_Revision01', 'control_ISRSA','visualizations')
if not os.path.exists(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    print('Directory %s created' % out_dir)
## location of group mask
mask_path = os.path.join(proj_path, 'MRI', 'groupmask_movies.nii.gz')

## get brain parcellation (k = 210; Brainnetome)
mask_name = 'Brainnetome'
brainnetome_path = os.path.join(proj_path, 'MRI','Brainnetome_atlas', 'BN_Atlas_210_cortical_2mm.nii.gz')
mask = Brain_Data(brainnetome_path, mask = mask_path)
mask_x = expand_mask(mask)

## visualize betas and thresholded betas within glass brain and write niftis
tmp_df = pd.read_csv(os.path.join(r_path, 'ISRSA_random_movie_Features_Post' + '.csv'))
beta_brain = roi_to_brain(pd.Series(tmp_df.loc[:, 'statistic']), mask_x)
pval_fwe_brain = roi_to_brain(pd.Series(tmp_df.loc[:, 'pvalFWE']), mask_x)

## plot and write threshoded image
display = nplot.plot_glass_brain(threshold(beta_brain, pval_fwe_brain, thr=0.05).to_nifti(),
    colorbar = True, plot_abs = False, vmin = -6.00, vmax = 6.00, cmap = 'inferno', threshold=1e-12)
plt.savefig(os.path.join(out_dir, '%s_pFWE005.png' % ('ISRSA_random_movie_features_post')), dpi = 400); plt.close()
