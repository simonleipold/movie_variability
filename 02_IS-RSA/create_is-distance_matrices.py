#!/usr/bin/env python
import os
import pandas as pd
import numpy as np

from nltools.data import Brain_Data, Adjacency
from nltools.mask import expand_mask

from sklearn.metrics import pairwise_distances

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
dir_out = os.path.join(projpath, 'Scripts', '04_2ndLev_ISRSA', 'matrices')
if not os.path.exists(os.path.join(dir_out)):
    os.makedirs(os.path.join(dir_out))
    print('Dir %s created ' % dir_out)

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
        similarity_matrix = pairwise_distances(data[:, :, parcel], metric = 'correlation') # correlation distance
        similarity_matrices.append(Adjacency(similarity_matrix, matrix_type='distance'))
        # put the ISC matrix into a Pandas DataFrame
        df = pd.DataFrame(similarity_matrix, index = subjlist['PID'], columns = subjlist['PID'])
        # save the ISC matrix as a CSV file
        df.to_csv(os.path.join(dir_out, '%s_parcel%s.csv' % (movie, parcel+1)), index = True, header = True)
