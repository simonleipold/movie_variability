#!/usr/bin/env python
import os
import numpy as np
import pandas as pd
from scipy import io as sio

## where are matrices located?
projpath = os.path.join('/project', '3011157.03', 'Simon', 'proj_2022_CABB_movie', 'DistanceMatrices')
## where should new matrices be stored?
dir_out = os.path.join('/project', '3011157.03', 'Simon', 'proj_2022_CABB_movie', 'Scripts', '04_2ndLev_ISRSA', 'matrices')
if not os.path.exists(dir_out):
    os.makedirs(dir_out, exist_ok = True)
    print('directory %s created' % (dir_out))

## where is the subjectlist
subjlist = pd.read_csv(os.path.join(projpath, 'subjlist.csv'), dtype = object)

## load-in the separate matrices
# Features
tmp_mat = sio.loadmat(os.path.join(projpath, 'features_Mahalanobis_large_matrix_56pairs'))
feat_mat_raw = tmp_mat['B2']
# Naming
tmp_mat = sio.loadmat(os.path.join(projpath, 'namesRDM.mat'))
nam_mat_excl_raw = tmp_mat['naming_RDM']

## prepare a matrix that will be used to identify the cells
rois = ['sub-%s-%s-%s' % (sub, t, i) for sub in subjlist['PID'] for t in ['pre', 'post'] for i in ['01',
'02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16']]
# tmp_df = pd.DataFrame(index = rois, columns = rois)
# for i in rois:
#     for j in rois:
#         tmp_df.loc[i, j] = i + ' <-> '  + j
# tmp_df = np.array(tmp_df)
# ## save matrix with identifiers
# sio.savemat(os.path.join(dir_out, 'namez_matrix.mat'), {'tmp_df': tmp_df})
## load matrix with identifiers
tmp_mat = sio.loadmat(os.path.join(dir_out, 'namez_matrix'), squeeze_me = True)
tmp_df = tmp_mat['tmp_df']
## extract upper triangle (including diagonal) from identifier matrix
namez = tmp_df[np.triu_indices(len(rois), k = 0)]

### reshape FEATURES matrix
## extract upper triangle (including diagonal) from features matrix
tmp_mat2 = feat_mat_raw[np.triu_indices(len(rois), k = 0)]
## join identifiers and values from features matrix
tmp_df2 = pd.DataFrame({'rois': namez, 'values': tmp_mat2})

## add column to dataset, which indicates pre or post matrix
def preorpost(wert):
    if not 'post' in wert:
        return 'pre'
    elif not 'pre' in wert:
        return 'post'
    else:
        return 'other'

tmp_df2['rois2'] = tmp_df2['rois'].map(preorpost)

## create diagonal-averaged pre matrix
tmp_df_pre = tmp_df2.loc[tmp_df2['rois2'] == "pre"].copy()
tmp_df_pre.reset_index(inplace = True, drop = True)
tmp_df_pre['subj1'] = tmp_df_pre.loc[:,'rois'].str.slice(0,7)
tmp_df_pre['subj2'] = tmp_df_pre.loc[:,'rois'].str.slice(19,26)
tmp_df_pre['pair'] = tmp_df_pre.loc[:,'subj1'] + tmp_df_pre.loc[:,'subj2']
tmp_df_pre['fribble1'] = tmp_df_pre.loc[:,'rois'].str.slice(8,14)
tmp_df_pre['fribble2'] = tmp_df_pre.loc[:,'rois'].str.slice(27,33)
# add column to dataset, which indicates which fribble
def sameordiff(datensatz):
    if datensatz['fribble1'] == datensatz['fribble2']:
        return 'same'
    else:
        return 'diff'
tmp_df_pre['fribble'] = tmp_df_pre.apply(sameordiff, axis = 1)
# only keep the same fribbles
tmp_df_pre_diag = tmp_df_pre.loc[tmp_df_pre['fribble'] == "same"].copy()
tmp_df_pre_diag.reset_index(inplace = True, drop = True)
# average the diagonal-averaged pre matrix
tmp_df_pre_diag_avg = tmp_df_pre_diag.groupby("pair").mean(numeric_only=True)
# create an array with the averaged values
tmp_df_pre_diag_avg['subj1'] = tmp_df_pre_diag_avg.index.str.slice(0,7)
tmp_df_pre_diag_avg['subj2'] = tmp_df_pre_diag_avg.index.str.slice(7,15)
tmp_arr = tmp_df_pre_diag_avg.set_index(['subj1', 'subj2'])['values'].unstack().values
feat_mat_pre_ref_diag = np.triu(tmp_arr) + np.triu(tmp_arr,1).T
np.fill_diagonal(feat_mat_pre_ref_diag, 0)
# put the matrix into a Pandas DataFrame
df = pd.DataFrame(feat_mat_pre_ref_diag, index = subjlist['PID'], columns = subjlist['PID'])
# save the ISC matrix as a CSV file
df.to_csv(os.path.join(dir_out, 'Features_pre.csv'), index = True, header = True)

## create diagonal-averaged post matrix
tmp_df_post = tmp_df2.loc[tmp_df2['rois2'] == "post"].copy()
tmp_df_post.reset_index(inplace = True, drop = True)
tmp_df_post['subj1'] = tmp_df_post.loc[:,'rois'].str.slice(0,7)
tmp_df_post['subj2'] = tmp_df_post.loc[:,'rois'].str.slice(20,27)
tmp_df_post['pair'] = tmp_df_post.loc[:,'subj1'] + tmp_df_post.loc[:,'subj2']
tmp_df_post['fribble1'] = tmp_df_post.loc[:,'rois'].str.slice(8,15)
tmp_df_post['fribble2'] = tmp_df_post.loc[:,'rois'].str.slice(28,36)
tmp_df_post['fribble'] = tmp_df_post.apply(sameordiff, axis = 1)
tmp_df_post_diag = tmp_df_post.loc[tmp_df_post['fribble'] == "same"].copy()
tmp_df_post_diag.reset_index(inplace = True, drop = True)
tmp_df_post_diag_avg = tmp_df_post_diag.groupby("pair").mean(numeric_only=True)
tmp_df_post_diag_avg['subj1'] = tmp_df_post_diag_avg.index.str.slice(0,7)
tmp_df_post_diag_avg['subj2'] = tmp_df_post_diag_avg.index.str.slice(7,15)
tmp_arr = tmp_df_post_diag_avg.set_index(['subj1', 'subj2'])['values'].unstack().values
feat_mat_post_ref_diag = np.triu(tmp_arr) + np.triu(tmp_arr,1).T
np.fill_diagonal(feat_mat_post_ref_diag, 0)
df = pd.DataFrame(feat_mat_post_ref_diag, index = subjlist['PID'], columns = subjlist['PID'])
df.to_csv(os.path.join(dir_out, 'Features_post.csv'), index = True, header = True)

### reshape NAMING matrix
## extract upper triangle (including diagonal) from naming matrix
tmp_mat2 = nam_mat_excl_raw[np.triu_indices(len(rois), k = 0)]
tmp_df2 = pd.DataFrame({'rois': namez, 'values': tmp_mat2})
tmp_df2['rois2'] = tmp_df2['rois'].map(preorpost)
## create diagonal-averaged pre matrix
tmp_df_pre = tmp_df2.loc[tmp_df2['rois2'] == "pre"].copy()
tmp_df_pre.reset_index(inplace = True, drop = True)
tmp_df_pre['subj1'] = tmp_df_pre.loc[:,'rois'].str.slice(0,7)
tmp_df_pre['subj2'] = tmp_df_pre.loc[:,'rois'].str.slice(19,26)
tmp_df_pre['pair'] = tmp_df_pre.loc[:,'subj1'] + tmp_df_pre.loc[:,'subj2']
tmp_df_pre['fribble1'] = tmp_df_pre.loc[:,'rois'].str.slice(8,14)
tmp_df_pre['fribble2'] = tmp_df_pre.loc[:,'rois'].str.slice(27,33)
tmp_df_pre['fribble'] = tmp_df_pre.apply(sameordiff, axis = 1)
tmp_df_pre_diag = tmp_df_pre.loc[tmp_df_pre['fribble'] == "same"].copy()
tmp_df_pre_diag.reset_index(inplace = True, drop = True)
tmp_df_pre_diag_avg = tmp_df_pre_diag.groupby("pair").mean(numeric_only=True)
tmp_df_pre_diag_avg['subj1'] = tmp_df_pre_diag_avg.index.str.slice(0,7)
tmp_df_pre_diag_avg['subj2'] = tmp_df_pre_diag_avg.index.str.slice(7,15)
tmp_arr = tmp_df_pre_diag_avg.set_index(['subj1', 'subj2'])['values'].unstack().values
nam_mat_excl_pre_ref_diag = np.triu(tmp_arr) + np.triu(tmp_arr,1).T
np.fill_diagonal(nam_mat_excl_pre_ref_diag, 0)
df = pd.DataFrame(nam_mat_excl_pre_ref_diag, index = subjlist['PID'], columns = subjlist['PID'])
df.to_csv(os.path.join(dir_out, 'Naming_pre.csv'), index = True, header = True)

## create full, averaged, and diagonal-averaged post matrix
tmp_df_post = tmp_df2.loc[tmp_df2['rois2'] == "post"].copy()
tmp_df_post.reset_index(inplace = True, drop = True)
tmp_df_post['subj1'] = tmp_df_post.loc[:,'rois'].str.slice(0,7)
tmp_df_post['subj2'] = tmp_df_post.loc[:,'rois'].str.slice(20,27)
tmp_df_post['pair'] = tmp_df_post.loc[:,'subj1'] + tmp_df_post.loc[:,'subj2']
tmp_df_post['fribble1'] = tmp_df_post.loc[:,'rois'].str.slice(8,15)
tmp_df_post['fribble2'] = tmp_df_post.loc[:,'rois'].str.slice(28,36)
tmp_df_post['fribble'] = tmp_df_post.apply(sameordiff, axis = 1)
tmp_df_post_diag = tmp_df_post.loc[tmp_df_post['fribble'] == "same"].copy()
tmp_df_post_diag.reset_index(inplace = True, drop = True)
tmp_df_post_diag_avg = tmp_df_post_diag.groupby("pair").mean(numeric_only=True)
tmp_df_post_diag_avg['subj1'] = tmp_df_post_diag_avg.index.str.slice(0,7)
tmp_df_post_diag_avg['subj2'] = tmp_df_post_diag_avg.index.str.slice(7,15)
tmp_arr = tmp_df_post_diag_avg.set_index(['subj1', 'subj2'])['values'].unstack().values
nam_mat_excl_post_diag_ref = np.triu(tmp_arr) + np.triu(tmp_arr,1).T
np.fill_diagonal(nam_mat_excl_post_diag_ref, 0)
df = pd.DataFrame(nam_mat_excl_post_diag_ref, index = subjlist['PID'], columns = subjlist['PID'])
df.to_csv(os.path.join(dir_out, 'Naming_post.csv'), index = True, header = True)