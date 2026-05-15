#!/usr/bin/env python3
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
proj_path = '/project/3011157.03/Simon/proj_2022_CABB_movie'

# location of R output files to visualize
r_path = os.path.join(
    proj_path,
    'Scripts',
    'MovVar_ImagNeuro_Revision01',
    'Emofilm',
    'r_output_ISRSA'
)

# location where visualizations and niftis will be stored
out_dir = os.path.join(
    proj_path,
    'Scripts',
    'MovVar_ImagNeuro_Revision01',
    'Emofilm',
    'visualizations_ISRSA'
)
if not os.path.exists(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    print(f'Directory {out_dir} created')

# location of group mask
mask_path = os.path.join(proj_path, 'MRI', 'groupmask_movies_emofilm.nii.gz')

# ------------------------------------------------------------------
# atlas
# ------------------------------------------------------------------
brainnetome_path = os.path.join(
    proj_path,
    'MRI',
    'Brainnetome_atlas',
    'BN_Atlas_210_cortical_2mm.nii.gz'
)

mask = Brain_Data(brainnetome_path, mask=mask_path)
mask_x = expand_mask(mask)

# ------------------------------------------------------------------
# movies
# ------------------------------------------------------------------
movie_list = [f"movie{i}" for i in range(1, 15)]

# ------------------------------------------------------------------
# visualize betas/statistics and thresholded maps
# ------------------------------------------------------------------
for movie in movie_list:
    print(movie)

    in_file = os.path.join(r_path, f'ISRSA_personality_{movie}.csv')
    if not os.path.exists(in_file):
        print(f'File not found: {in_file}')
        continue

    tmp_df = pd.read_csv(in_file)

    # map parcelwise values back to brain
    stat_brain = roi_to_brain(pd.Series(tmp_df['statistic']), mask_x)
    pval_fdr_brain = roi_to_brain(pd.Series(tmp_df['pvalFDR']), mask_x)
    pval_fwe_brain = roi_to_brain(pd.Series(tmp_df['pvalFWE']), mask_x)

    # --------------------------------------------------------------
    # unthresholded plot
    # --------------------------------------------------------------
    nplot.plot_glass_brain(
        stat_brain.to_nifti(),
        colorbar=True,
        plot_abs=False,
        cmap='inferno',
        vmin=-6.0,
        vmax=6.0,
        threshold=1e-12
    )
    plt.savefig(
        os.path.join(out_dir, f'ISRSA_personality_{movie}_unthresholded.png'),
        dpi=400
    )
    plt.close()

    # --------------------------------------------------------------
    # thresholded plot (FWE < .05)
    # --------------------------------------------------------------
    thr_img = threshold(stat_brain, pval_fwe_brain, thr=0.05)

    nplot.plot_glass_brain(
        thr_img.to_nifti(),
        colorbar=True,
        plot_abs=False,
        cmap='inferno',
        vmin=-6.0,
        vmax=6.0,
        threshold=1e-12
    )
    plt.savefig(
        os.path.join(out_dir, f'ISRSA_personality_{movie}_pFWE005.png'),
        dpi=400
    )
    plt.close()

    # --------------------------------------------------------------
    # optional: save nifti files
    # --------------------------------------------------------------
    # stat_brain.write(os.path.join(out_dir, f'ISRSA_personality_{movie}_stat.nii.gz'))
    # thr_img.write(os.path.join(out_dir, f'ISRSA_personality_{movie}_pFWE005.nii.gz'))
