#!/usr/bin/env python
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from nltools.data import Brain_Data, Adjacency
from nltools.mask import expand_mask, roi_to_brain
from nltools.stats import threshold

from nilearn import plotting as nplot
from sklearn.metrics import pairwise_distances
from statsmodels.stats.multitest import fdrcorrection  # Import for FDR correction

## location of main project directory on HPC
projpath = '/project/3011157.03/Simon/proj_2022_CABB_movie/'
print('The main project directory is located here: %s' % projpath)
## location of preprocessed BIDS data
fmriprep_dir = os.path.join(projpath, 'MRI', 'BIDS_movie')
## location of subjectlist
subjlist = pd.read_csv(os.path.join(projpath, 'MRI', 'subjectlist.csv'), dtype = object)
## location of group mask
mask_path = os.path.join(projpath, 'MRI', 'groupmask_movies.nii.gz')
## get brain parcellation (k = 210 cortical parcels; "Brainnetome" atlas, Fan et al. 2016, Cerebral Cortex)
mask_name = 'Brainnetome'
brainnetome_path = os.path.join(projpath, 'MRI', 'Brainnetome_atlas', 'BN_Atlas_210_cortical_2mm.nii.gz')
mask = Brain_Data(brainnetome_path, mask = mask_path)
mask_x = expand_mask(mask)
atlas_labels = pd.read_csv(os.path.join(projpath, 'MRI', 'Brainnetome_atlas/Brainnetome_labels_cortical.csv'))

## location of extracted movie fMRI time series
mov_csv_path = os.path.join(fmriprep_dir, 'derivatives', 'secLev_nltools_ISC_ROI', mask_name, 'csv_files')

## where should the ISC matrices be stored?
dir_out = os.path.join(projpath, 'Scripts', '03_2ndLev_ISC', 'matrices')
if not os.path.exists(os.path.join(dir_out)):
    os.makedirs(os.path.join(dir_out))
    print('Dir %s created ' % dir_out)

## where should the visualizations be stored?
dir_out_vis = os.path.join(projpath, 'Scripts', '03_2ndLev_ISC', 'visualizations')
if not os.path.exists(os.path.join(dir_out_vis)):
    os.makedirs(os.path.join(dir_out_vis))
    print('Dir %s created ' % dir_out_vis)

## where should the csv results be stored?
dir_out_bootstrap = os.path.join(projpath, 'Scripts', '03_2ndLev_ISC', 'py_output_permutation')

# create ISC matrices for each movie
movie_list = ['movie1', 'movie2', 'movie3', 'movie4', 'movie5', 'movie6', 'movie7', 'movie8']
# load the extracted time series for each movie
for movie in movie_list:
    sub_timeseries = [] # list to store the time series for each subject
    for subj in subjlist['PID']:
        # print('Loading data for Subject Nr. %s'% (subj))
        sub_data = pd.read_csv(os.path.join(mov_csv_path, 'sub%s_%s_Average_ROI.csv' % (subj, movie)))
        sub_timeseries.append(sub_data.values)
    data = np.array(sub_timeseries)
    n_subs, n_ts, n_parcels = data.shape
    # calculate the ISC matrix for each parcel
    similarity_matrices = [] # list to store the ISC matrices for each parcel
    for parcel in range(n_parcels):
        # calculate the pairwise similarity between subjects
        similarity_matrix = 1 - pairwise_distances(data[:, :, parcel], metric = 'correlation')
        similarity_matrices.append(Adjacency(similarity_matrix, matrix_type='similarity'))
        # put the ISC matrix into a Pandas DataFrame
        df = pd.DataFrame(similarity_matrix, index = subjlist['PID'], columns = subjlist['PID'])
        # save the ISC matrix as a CSV file
        df.to_csv(os.path.join(dir_out, 'ISC_%s_parcel%s.csv' % (movie, parcel+1)), index = True, header = True)
    ## generate a visualization of the mean ISC matrix across subjects
    # extract the mean ISC values across subjects from the similarity matrices and put them into a dictionary
    isc = {parcel:similarity_matrices[parcel].isc(metric='mean', n_bootstraps=1, n_jobs=1)['isc'] for parcel in range(n_parcels)}
    isc_brain = roi_to_brain(pd.Series(isc), expand_mask(mask))
    nplot.plot_glass_brain(isc_brain.to_nifti(),
        colorbar = True, plot_abs = False,
        cmap = "viridis",
        vmin = -0.5, vmax = 0.5)
    plt.savefig(os.path.join(dir_out_vis, 'Mean_ISC_%s.png' % movie), dpi = 400)
    plt.close()
    ## statistical testing of the ISC values
    # calculate bootstrapped p-values for the ISC values
    p = {parcel:similarity_matrices[parcel].isc(metric='mean', n_bootstraps=10000, n_jobs=1)['p'] for parcel in range(n_parcels)}
    # create a Pandas DataFrame with the ISC values and p-values
    df = pd.DataFrame({'ISC':isc, 'p':p})
    # add column with Bonferroni-corrected p-values
    df['p_fwe'] = df['p'] * n_parcels
    # Add column with FDR-corrected p-values
    reject, p_fdr = fdrcorrection(df['p'], alpha=0.05)
    df['p_fdr'] = p_fdr
    # add the parcel numbers to the DataFrame
    df['parcel'] = np.arange(1, n_parcels+1)
    # add the parcel names to the DataFrame
    df['label'] = atlas_labels['label']
    # reorder the columns
    df = df[['parcel', 'label', 'ISC', 'p', 'p_fwe', 'p_fdr']]
    # save the DataFrame as a CSV file
    df.to_csv(os.path.join(dir_out_bootstrap, 'ISC_%s.csv' % movie), index = False)
    ## generate a visualization of the mean ISC matrix only for significant parcels
    # pval_brain = roi_to_brain(pd.Series(df.loc[:, 'p_fwe']), mask_x)
    # display = nplot.plot_glass_brain(threshold(isc_brain, pval_brain, thr=0.05).to_nifti(),
    #     cmap = "viridis", colorbar = True, plot_abs = False, vmin = -0.5, vmax = 0.5,
    #     )
    ## Save the plot to a file
    # plt.savefig(os.path.join(dir_out_vis, 'Mean_ISC_%s_thresholded.png' % movie), dpi = 400); plt.close()

