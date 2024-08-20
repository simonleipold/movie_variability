#!/usr/bin/env python
import os
import pandas as pd
import matplotlib.pyplot as plt

from nltools.data import Brain_Data
from nltools.mask import expand_mask

from nilearn import plotting as nplot

import warnings
warnings.filterwarnings("ignore") # suppress warnings

## location of main project directory on HPC
projpath = '/project/3011157.03/Simon/proj_2022_CABB_movie/MRI'
print('The main project directory is located here: %s' % projpath)
## location of preprocessed BIDS data
fmriprep_dir = os.path.join(projpath, 'BIDS_movie')
## location of preprocessed, denoised, and smoothed data
movpath = os.path.join(fmriprep_dir, 'derivatives','nilearn')
## location of subjectlist
subjlist = pd.read_csv(os.path.join(projpath, 'subjectlist.csv'), dtype = object)
## location of group mask
mask_path = os.path.join(projpath, 'groupmask_movies.nii.gz')

## get brain parcellation (k = 210 cortical parcels; "Brainnetome" atlas, Fan et al. 2016, Cerebral Cortex)
mask_name = 'Brainnetome'
brainnetome_path = os.path.join(projpath, 'Brainnetome_atlas', 'BN_Atlas_210_cortical_2mm.nii.gz')
mask = Brain_Data(brainnetome_path, mask = mask_path)
mask_x = expand_mask(mask)
atlas_labels = pd.read_csv(os.path.join(projpath, 'Brainnetome_atlas/Brainnetome_labels_cortical.csv'))

## where should the results be stored?
dir_out = os.path.join(fmriprep_dir, 'derivatives', 'secLev_nltools_ISC_ROI', mask_name)
if not os.path.exists(os.path.join(dir_out)):
    os.makedirs(os.path.join(dir_out))
    print('Dir %s created ' % dir_out)

plot_atlas = True # set to true if you want to plot the atlas
if plot_atlas:
    nplot.plot_roi(
        mask.to_nifti(),
        title='%s Parcellation' % mask_name)
    plt.savefig(os.path.join(dir_out, 'CorticalParcels_%s.png' % mask_name))
    plt.close()


## extract average activation from atlas and save to csv
extract_csv = True # set to false if csv files have already been created
## location of csv files
dir_out_csv = os.path.join(dir_out, 'csv_files')
if extract_csv:
    if not os.path.exists(dir_out_csv):
        os.makedirs(dir_out_csv)
        print('Dir %s created ' % dir_out_csv)
    for scan in ['movie1', 'movie2', 'movie3', 'movie4', 'movie5', 'movie6', 'movie7', 'movie8']:
        for subj in subjlist['PID']:
            # print('Loading data for Subject Nr. %s'% (subj))
            data = Brain_Data(os.path.join(movpath, 'sub-%s' % subj, 's_%s_img.nii.gz' % (scan)), mask = mask_path)
            roi = data.extract_roi(mask)
            pd.DataFrame(roi.T).to_csv(os.path.join(dir_out_csv, 'sub%s_%s_Average_ROI.csv' % (subj, scan)),
                index = False)
