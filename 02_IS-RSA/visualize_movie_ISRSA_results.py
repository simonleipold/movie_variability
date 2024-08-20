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
r_path = os.path.join(proj_path, 'Scripts', '04_2ndLev_ISRSA','r_output')
## location where visualizations and niftis will be stored
out_dir = os.path.join(proj_path, 'Scripts', '04_2ndLev_ISRSA','visualizations')
if not os.path.exists(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    print('Directory %s created' % out_dir)
## location of group mask
mask_path = os.path.join(proj_path, 'MRI', 'groupmask_movies.nii.gz')

## create a file list
tmp_list = os.listdir(r_path)
file_list = []
for f in tmp_list:
    if '.csv' in f:
        file_list.append(f)
file_list.sort()
print(file_list)
## create a task list for plots and files
task_flist = ['ISRSA_features_post_', 'ISRSA_features_pre_', 'ISRSA_naming_post_', 'ISRSA_naming_pre_']

## get brain parcellation (k = 210; Brainnetome)
mask_name = 'Brainnetome'
brainnetome_path = os.path.join(proj_path, 'MRI','Brainnetome_atlas', 'BN_Atlas_210_cortical_2mm.nii.gz')
mask = Brain_Data(brainnetome_path, mask = mask_path)
mask_x = expand_mask(mask)

## visualize betas and thresholded betas within glass brain and write niftis
for i, f in enumerate(task_flist):
    for j, m in enumerate(["movie1", "movie2", "movie3", "movie4", "movie5", "movie6", "movie7", "movie8"]):
        print(f)
        print(m)
        tmp_df = pd.read_csv(os.path.join(r_path, f + m + '.csv'))
        # beta_brain = roi_to_brain(pd.Series(tmp_df.loc[:, 'Beta']), mask_x)
        beta_brain = roi_to_brain(pd.Series(tmp_df.loc[:, 'statistic']), mask_x)
        pval_brain = roi_to_brain(pd.Series(tmp_df.loc[:, 'pvalFDR']), mask_x)
        pval_fwe_brain = roi_to_brain(pd.Series(tmp_df.loc[:, 'pvalFWE']), mask_x)

        ## plot and write unthreshoded image
        # nplot.plot_glass_brain(beta_brain.to_nifti(),
        #     colorbar = True, plot_abs = False, vmin = -0.10, vmax = 0.10, cmap = 'coolwarm')
        # plt.savefig(os.path.join(out_dir, '%s%s.png' % (f, m))); plt.close()
        # beta_brain.to_nifti().to_filename(os.path.join(out_dir, '%s%s.nii.gz' % (f, m)))

        ## plot and write threshoded image
        display = nplot.plot_glass_brain(threshold(beta_brain, pval_fwe_brain, thr=0.05).to_nifti(),
            # colorbar = True, plot_abs = False, vmin = -0.10, vmax = 0.10, cmap = 'coolwarm',
            colorbar = True, plot_abs = False, vmin = -6.00, vmax = 6.00, cmap = 'inferno')
        # display.add_contours(threshold(beta_brain, pval_fwe_brain, thr=0.05).to_nifti(), colors = 'gray')
        plt.savefig(os.path.join(out_dir, '%s%s_pFWE005.png' % (f, m)), dpi = 400); plt.close()
        # threshold(beta_brain, pval_brain, thr=0.05).to_nifti().to_filename(os.path.join(out_dir, '%s%s_qFDR005.nii.gz' % (f, m)))
        # threshold(beta_brain, pval_fwe_brain, thr=0.05).to_nifti().to_filename(os.path.join(out_dir, '%s%s_pFWE005.nii.gz' % (f, m)))