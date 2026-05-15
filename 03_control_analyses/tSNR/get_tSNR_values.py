#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from nilearn.image import load_img, index_img, resample_to_img, math_img
from nilearn import plotting as nplot

from nltools.data import Brain_Data
from nltools.mask import expand_mask

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
project_root = '/project/3011157.03/Simon/proj_2022_CABB_movie'
proj_path = os.path.join(project_root, 'MRI')

fmriprep_dir = os.path.join(
    proj_path,
    'BIDS_movie',
    'derivatives',
    'fmriprep'
)

logfile_dir = os.path.join(
    proj_path,
    'Logfiles',
    'Movies',
    'reformatted'
)

subjlist_file = os.path.join(proj_path, 'subjectlist.csv')

out_dir = os.path.join(
    project_root,
    'Scripts',
    'MovVar_ImagNeuro_Revision01',
    'control_tSNR'
)

out_csv_dir = os.path.join(out_dir, 'csv_files')
out_map_dir = os.path.join(out_dir, 'tsnr_maps')
out_group_map_dir = os.path.join(out_dir, 'group_mean_tsnr_maps')
out_vis_dir = os.path.join(out_dir, 'visualizations')
out_resample_dir = os.path.join(out_dir, 'resampled_mask_atlas')

for d in [
    out_dir,
    out_csv_dir,
    out_map_dir,
    out_group_map_dir,
    out_vis_dir,
    out_resample_dir
]:
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------
# Original group mask and atlas
# ------------------------------------------------------------
group_mask_in = os.path.join(
    proj_path,
    'groupmask_movies.nii.gz'
)

brainnetome_in = os.path.join(
    proj_path,
    'Brainnetome_atlas',
    'BN_Atlas_210_cortical_2mm.nii.gz'
)

group_mask_resampled = os.path.join(
    out_resample_dir,
    'groupmask_movies_space-MNI152NLin2009cAsym_res-2.nii.gz'
)

brainnetome_resampled = os.path.join(
    out_resample_dir,
    'BN_Atlas_210_cortical_space-MNI152NLin2009cAsym_res-2.nii.gz'
)

resample_check_plot = os.path.join(
    out_resample_dir,
    'groupmask_brainnetome_resampled_check.png'
)

# ------------------------------------------------------------
# Subject list
# ------------------------------------------------------------
subjlist = pd.read_csv(subjlist_file, dtype=object)

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def get_func_file(subj):
    return os.path.join(
        fmriprep_dir,
        f'sub-{subj}',
        'ses-mri01',
        'func',
        f'sub-{subj}_ses-mri01_task-movies_run-1_echo-1_'
        f'space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz'
    )


def get_timing_file(subj):
    return os.path.join(
        logfile_dir,
        f'{subj}_timing.csv'
    )

# ------------------------------------------------------------
# Resample group mask and atlas to fMRIPrep BOLD grid
# ------------------------------------------------------------
print('Finding target fMRIPrep BOLD image for resampling...')

target_func_file = None

for subj in subjlist['PID']:
    candidate = get_func_file(subj)

    if os.path.exists(candidate):
        target_func_file = candidate
        print(f'Using target image from subject {subj}: {target_func_file}')
        break

if target_func_file is None:
    raise FileNotFoundError(
        'No fMRIPrep BOLD file found for any subject in subjectlist.'
    )

target_4d = load_img(target_func_file)
target_img = index_img(target_4d, 0)

print('Resampling group mask to fMRIPrep BOLD grid...')

mask_img = load_img(group_mask_in)

mask_res = resample_to_img(
    mask_img,
    target_img,
    interpolation='nearest',
    force_resample=True,
    copy_header=True
)

# Binarize after resampling
mask_res_bin = math_img('img > 0', img=mask_res)
mask_res_bin.to_filename(group_mask_resampled)

print(f'Saved resampled group mask: {group_mask_resampled}')

print('Resampling Brainnetome atlas to fMRIPrep BOLD grid...')

atlas_img = load_img(brainnetome_in)

atlas_res = resample_to_img(
    atlas_img,
    target_img,
    interpolation='nearest',
    force_resample=True,
    copy_header=True
)

atlas_res.to_filename(brainnetome_resampled)

print(f'Saved resampled Brainnetome atlas: {brainnetome_resampled}')

# Sanity-check plot
display = nplot.plot_roi(
    atlas_res,
    bg_img=mask_res_bin,
    title='Brainnetome atlas and group mask resampled to fMRIPrep BOLD grid',
    display_mode='ortho',
    cut_coords=(0, 0, 0)
)

plt.savefig(resample_check_plot, dpi=300, bbox_inches='tight')
plt.close()

print(f'Saved resampling check plot: {resample_check_plot}')

# ------------------------------------------------------------
# Atlas labels
# ------------------------------------------------------------
labels_csv = os.path.join(
    proj_path,
    'Brainnetome_atlas',
    'Brainnetome_labels_cortical.csv'
)

labels_df = pd.read_csv(labels_csv)
labels_df = labels_df.rename(columns={'one_based': 'Parcel'})

network_mapping = {
    0: 'NA',
    1: 'Visual',
    2: 'Somatomotor',
    3: 'Dorsal Attention',
    4: 'Ventral Attention',
    5: 'Limbic',
    6: 'Frontoparietal',
    7: 'Default'
}

labels_df['Yeo_7network'] = labels_df['Yeo_7network'].replace(network_mapping)

# ------------------------------------------------------------
# Load resampled atlas with resampled group mask
# ------------------------------------------------------------
atlas = Brain_Data(
    brainnetome_resampled,
    mask=group_mask_resampled
)

atlas_expanded = expand_mask(atlas)
n_nodes = len(atlas_expanded)

if len(labels_df) != n_nodes:
    raise ValueError(
        f'Number of atlas labels ({len(labels_df)}) does not match '
        f'number of atlas parcels ({n_nodes}).'
    )

# ------------------------------------------------------------
# Settings
# ------------------------------------------------------------
movie_list = [f'movie{i}' for i in range(1, 9)]

tsnr_maps_by_movie = {movie: [] for movie in movie_list}
all_tsnr_rows = []

# ------------------------------------------------------------
# Main loop
# ------------------------------------------------------------
for subj in subjlist['PID']:

    print(f'Processing subject {subj}')

    func_file = get_func_file(subj)
    timing_file = get_timing_file(subj)

    if not os.path.exists(func_file):
        raise FileNotFoundError(f'Missing preprocessed BOLD file: {func_file}')

    if not os.path.exists(timing_file):
        raise FileNotFoundError(f'Missing timing file: {timing_file}')

    print(f'Using BOLD file: {func_file}')
    print(f'Using timing file: {timing_file}')

    # Load BOLD data using the resampled group mask
    bold_data = Brain_Data(
        func_file,
        mask=group_mask_resampled
    )

    log = pd.read_csv(timing_file)

    subj_map_dir = os.path.join(out_map_dir, f'sub-{subj}')
    os.makedirs(subj_map_dir, exist_ok=True)

    for i, movie in enumerate(movie_list):

        print(f'  Processing {movie}')

        onset = int(log.loc[i, 'Onset']) - 1
        offset = int(log.loc[i, 'Offset']) - 1

        movie_data = bold_data[onset:offset]

        # Calculate voxelwise tSNR
        # Brain_Data.mean() and Brain_Data.std() operate across time/images
        tsnr_movie = movie_data.mean() / movie_data.std()

        # Clean up inf/nan values from zero-SD voxels, if any
        tsnr_movie.data[~np.isfinite(tsnr_movie.data)] = 0

        # Save subject-level movie tSNR map
        tsnr_map_file = os.path.join(
            subj_map_dir,
            f'sub-{subj}_{movie}_tSNR.nii.gz'
        )

        tsnr_movie.to_nifti().to_filename(tsnr_map_file)
        print(f'  Saved map: {tsnr_map_file}')

        # Store voxelwise map for movie-wise group average
        tsnr_maps_by_movie[movie].append(tsnr_movie)

        # Extract parcel-wise tSNR
        parcel_tsnr = tsnr_movie.extract_roi(atlas)

        tmp = labels_df.copy()
        tmp.insert(0, 'Movie', movie)
        tmp.insert(0, 'PID', subj)
        tmp['tSNR'] = parcel_tsnr

        all_tsnr_rows.append(tmp)

# ------------------------------------------------------------
# Save full parcel-wise tSNR table
# ------------------------------------------------------------
tsnr_df = pd.concat(all_tsnr_rows, ignore_index=True)

tsnr_outfile = os.path.join(
    out_csv_dir,
    'parcel_tSNR_all_subjects_movies.csv'
)

tsnr_df.to_csv(tsnr_outfile, index=False)
print(f'Saved full parcel-wise tSNR table: {tsnr_outfile}')

# ------------------------------------------------------------
# Average parcel-wise tSNR across participants
# ------------------------------------------------------------
group_cols = [
    'Movie',
    'Parcel',
    'zero_based',
    'label',
    'Yeo_7network',
    'Yeo_17network'
]

mean_tsnr_df = (
    tsnr_df
    .groupby(group_cols, as_index=False)
    .agg(
        Mean_tSNR=('tSNR', 'mean'),
        SD_tSNR=('tSNR', 'std'),
        N=('tSNR', 'count')
    )
)

# Make sure Movie is first in the mean CSV
mean_tsnr_df = mean_tsnr_df[
    [
        'Movie',
        'Parcel',
        'zero_based',
        'label',
        'Yeo_7network',
        'Yeo_17network',
        'Mean_tSNR',
        'SD_tSNR',
        'N'
    ]
]

mean_outfile = os.path.join(
    out_csv_dir,
    'parcel_tSNR_mean_across_subjects.csv'
)

mean_tsnr_df.to_csv(mean_outfile, index=False)
print(f'Saved mean parcel-wise tSNR table: {mean_outfile}')

# ------------------------------------------------------------
# Create movie-wise group-average voxelwise tSNR maps
# ------------------------------------------------------------
group_mean_maps = {}

for movie in movie_list:

    print(f'Creating group mean voxelwise tSNR map for {movie}')

    movie_tsnr_bd = Brain_Data(tsnr_maps_by_movie[movie])
    movie_tsnr_mean = movie_tsnr_bd.mean()

    group_mean_maps[movie] = movie_tsnr_mean

    group_map_file = os.path.join(
        out_group_map_dir,
        f'Mean_tSNR_{movie}.nii.gz'
    )

    movie_tsnr_mean.to_nifti().to_filename(group_map_file)
    print(f'Saved group mean map: {group_map_file}')

# ------------------------------------------------------------
# Glass-brain visualizations per movie
# ------------------------------------------------------------
all_mean_values = np.concatenate([
    group_mean_maps[movie].data.flatten()
    for movie in movie_list
])

finite_values = all_mean_values[np.isfinite(all_mean_values)]

vmin = 0
vmax = np.nanpercentile(finite_values, 95)

for movie in movie_list:

    print(f'Creating glass brain for {movie}')

    display = nplot.plot_glass_brain(
        group_mean_maps[movie].to_nifti(),
        colorbar=True,
        plot_abs=False,
        cmap='viridis',
        vmin=vmin,
        vmax=vmax,
        title=f'Mean tSNR: {movie}'
    )

    outfile = os.path.join(
        out_vis_dir,
        f'Mean_tSNR_{movie}_glassbrain.png'
    )

    display.savefig(outfile, dpi=400)
    display.close()

    print(f'Saved: {outfile}')

print('All done.')