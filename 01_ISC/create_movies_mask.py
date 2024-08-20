#!/usr/bin/env python
import os
import pandas as pd

from nilearn import masking as nmask
from bids.layout import BIDSLayout


### create mask across subjects

# project location
proj_path = '/project/3011157.03/Simon/proj_2022_CABB_movie/MRI'

# location of movie data
fmriprep_path = os.path.join(proj_path, 'BIDS_movie')

# location of preprocessed, denoised, and smoothed data
mov_path = os.path.join(fmriprep_path, 'derivatives','nilearn')

# location of subjectlist
subjlist = pd.read_csv(os.path.join(proj_path, 'subjectlist.csv'), dtype = object)

# where should mask be stored?
dir_out = proj_path

# get all paths
layout = BIDSLayout(fmriprep_path, derivatives = True)

# get paths of masks per subject
mask_list = []
for subj in subjlist['PID']:
    func_mask_files = layout.get(subject = subj, datatype = 'func',
    suffix = 'mask', desc = 'brain', space = 'MNI152NLin2009cAsym',
    extension = "nii.gz", return_type = 'filename')
    mask_list.append(func_mask_files[0])

## calculate a group mask using the conjunction of all subjects
groupmask = nmask.intersect_masks(mask_list, threshold = 0.8)
groupmask.to_filename(os.path.join(dir_out, 'groupmask_movies.nii.gz'))
